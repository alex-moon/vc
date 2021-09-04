import os
from functools import reduce
from operator import mul

import cv2
import numpy as np
import torch
from skimage.transform import resize

try:
    import cynetworkx as netx
except ImportError:
    import networkx as netx
import imageio
import copy
from collections import namedtuple


# @todo put all in class and clean up

def open_small_mask(mask, context, open_iteration, kernel):
    np_mask = mask.cpu().data.numpy().squeeze().astype(np.uint8)
    np_context = context.cpu().data.numpy().squeeze().astype(np.uint8)
    np_input = np_mask + np_context
    for _ in range(open_iteration):
        np_input = cv2.erode(
            cv2.dilate(np_input, np.ones((kernel, kernel)), iterations=1),
            np.ones((kernel, kernel)),
            iterations=1
        )
    np_mask[(np_input - np_context) > 0] = 1
    out_mask = torch.FloatTensor(np_mask).to(mask)[None, None, ...]

    return out_mask


def filter_irrelevant_edge(
    self_edge,
    comp_edge,
    other_edges,
    other_edges_with_id,
    context,
    depth,
    mesh,
    context_cc
):
    other_edges = other_edges.squeeze().astype(np.uint8)
    other_edges_with_id = other_edges_with_id.squeeze()
    self_edge = self_edge.squeeze()
    dilate_bevel_self_edge = cv2.dilate(
        (self_edge + comp_edge).astype(np.uint8),
        np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]]),
        iterations=1
    )
    dilate_cross_self_edge = cv2.dilate(
        (self_edge + comp_edge).astype(np.uint8),
        np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]]).astype(np.uint8),
        iterations=1
    )
    edge_ids = np.unique(
        other_edges_with_id * context + (-1) * (1 - context)
    ).astype(np.int)
    end_depth_maps = np.zeros_like(self_edge)
    self_edge_ids = np.sort(
        np.unique(other_edges_with_id[self_edge > 0]).astype(np.int)
    )
    self_edge_ids = self_edge_ids[1:] if self_edge_ids.shape[0] > 0 and \
                                         self_edge_ids[
                                             0] == -1 else self_edge_ids
    self_comp_ids = np.sort(
        np.unique(other_edges_with_id[comp_edge > 0]).astype(np.int)
    )
    self_comp_ids = self_comp_ids[1:] if self_comp_ids.shape[0] > 0 and \
                                         self_comp_ids[
                                             0] == -1 else self_comp_ids
    edge_ids = edge_ids[1:] if edge_ids[0] == -1 else edge_ids
    other_edges_info = []
    extend_other_edges = np.zeros_like(other_edges)

    filter_self_edge = np.zeros_like(self_edge)
    for self_edge_id in self_edge_ids:
        filter_self_edge[other_edges_with_id == self_edge_id] = 1
    dilate_self_comp_edge = cv2.dilate(
        comp_edge,
        kernel=np.ones((3, 3)),
        iterations=2
    )
    valid_self_comp_edge = np.zeros_like(comp_edge)
    for self_comp_id in self_comp_ids:
        valid_self_comp_edge[self_comp_id == other_edges_with_id] = 1
    self_comp_edge = dilate_self_comp_edge * valid_self_comp_edge
    filter_self_edge = (filter_self_edge + self_comp_edge).clip(0, 1)
    for edge_id in edge_ids:
        other_edge_locs = (other_edges_with_id == edge_id).astype(np.uint8)
        condition = (other_edge_locs * other_edges * context.astype(np.uint8))
        end_cross_point = dilate_cross_self_edge * condition * (
            1 - filter_self_edge)
        end_bevel_point = dilate_bevel_self_edge * condition * (
            1 - filter_self_edge)
        if end_bevel_point.max() != 0:
            end_depth_maps[end_bevel_point != 0] = depth[end_bevel_point != 0]
            if end_cross_point.max() == 0:
                nxs, nys = np.where(end_bevel_point != 0)
                for nx, ny in zip(nxs, nys):
                    bevel_node = \
                        [xx for xx in context_cc if
                         xx[0] == nx and xx[1] == ny][0]
                for ne in mesh.neighbors(bevel_node):
                    if (
                        other_edges_with_id[ne[0], ne[1]] > -1
                        and dilate_cross_self_edge[ne[0], ne[1]] > 0
                    ):
                        extend_other_edges[ne[0], ne[1]] = 1
                        break
        else:
            other_edges[other_edges_with_id == edge_id] = 0
    other_edges = (other_edges + extend_other_edges).clip(0, 1) * context

    return other_edges, end_depth_maps, other_edges_info


def clean_far_edge(
    input_edge,
    end_depth_maps,
    mask,
    context,
    global_mesh,
    info_on_pix,
    self_edge,
    inpaint_id,
    args
):
    mesh = netx.Graph()
    hxs, hys = np.where(input_edge * mask > 0)
    valid_near_edge = (input_edge != 0).astype(np.uint8) * context
    valid_map = mask + context
    invalid_edge_ids = []
    for hx, hy in zip(hxs, hys):
        node = (hx, hy)
        mesh.add_node((hx, hy))
        eight_nes = [ne for ne in
                     [(hx + 1, hy), (hx - 1, hy), (hx, hy + 1), (hx, hy - 1), \
                      (hx + 1, hy + 1), (hx - 1, hy - 1), (hx - 1, hy + 1),
                      (hx + 1, hy - 1)] \
                     if 0 <= ne[0] < input_edge.shape[0] and 0 <= ne[1] <
                     input_edge.shape[1] and 0 < input_edge[
                         ne[0], ne[1]]]  # or end_depth_maps[ne[0], ne[1]] != 0]
        for ne in eight_nes:
            mesh.add_edge(node, ne, length=np.hypot(ne[0] - hx, ne[1] - hy))
            if end_depth_maps[ne[0], ne[1]] != 0:
                mesh.nodes[ne[0], ne[1]]['cnt'] = True
                if end_depth_maps[ne[0], ne[1]] == 0:
                    pass
                mesh.nodes[ne[0], ne[1]]['depth'] = end_depth_maps[ne[0], ne[1]]
            elif mask[ne[0], ne[1]] != 1:
                four_nes = [
                    nne
                    for nne
                    in [
                        (ne[0] + 1, ne[1]),
                        (ne[0] - 1, ne[1]),
                        (ne[0], ne[1] + 1),
                        (ne[0], ne[1] - 1)
                    ]
                    if (
                        0 <= nne[0] < end_depth_maps.shape[0]
                        and 0 <= nne[1] < end_depth_maps.shape[1]
                    )
                ]
                for nne in four_nes:
                    if end_depth_maps[nne[0], nne[1]] != 0:
                        mesh.add_edge(
                            nne,
                            ne,
                            length=np.hypot(nne[0] - ne[0], nne[1] - ne[1])
                        )
                        mesh.nodes[nne[0], nne[1]]['cnt'] = True
                        mesh.nodes[nne[0], nne[1]]['depth'] = end_depth_maps[
                            nne[0], nne[1]]
    ccs = [*netx.connected_components(mesh)]
    end_pts = []
    for cc in ccs:
        end_pts.append(set())
        for node in cc:
            if mesh.nodes[node].get('cnt') is not None:
                end_pts[-1].add((node[0], node[1], mesh.nodes[node]['depth']))

    fpath_map = np.zeros_like(input_edge) - 1
    npath_map = np.zeros_like(input_edge) - 1
    npaths, fpaths = dict(), dict()
    end_idx = 0
    while end_idx < len(end_pts):
        end_pt, cc = [*zip(end_pts, ccs)][end_idx]
        end_idx += 1
        sorted_end_pt = []
        fpath = []
        iter_fpath = []
        if len(end_pt) > 2 or len(end_pt) == 0:
            if len(end_pt) > 2:
                continue
            continue
        if len(end_pt) == 2:
            ravel_end = [*end_pt]
            tmp_sub_mesh = mesh.subgraph(list(cc)).copy()
            tmp_npath = [*netx.shortest_path(
                tmp_sub_mesh,
                (ravel_end[0][0], ravel_end[0][1]),
                (ravel_end[1][0], ravel_end[1][1]),
                weight='length'
            )]
            fpath_map1, npath_map1, disp_diff1 = plan_path(
                mesh,
                info_on_pix,
                cc,
                ravel_end[0:1],
                global_mesh,
                input_edge,
                mask,
                valid_map,
                inpaint_id,
                npath_map=None,
                fpath_map=None,
                npath=tmp_npath
            )
            fpath_map2, npath_map2, disp_diff2 = plan_path(
                mesh,
                info_on_pix,
                cc,
                ravel_end[1:2],
                global_mesh,
                input_edge,
                mask,
                valid_map,
                inpaint_id,
                npath_map=None,
                fpath_map=None,
                npath=tmp_npath
            )
            tmp_disp_diff = [disp_diff1, disp_diff2]
            self_end = []
            ds_edge = cv2.dilate(
                self_edge.astype(np.uint8),
                np.ones((3, 3)),
                iterations=1
            )
            if ds_edge[ravel_end[0][0], ravel_end[0][1]] > 0:
                self_end.append(1)
            else:
                self_end.append(0)
            if ds_edge[ravel_end[1][0], ravel_end[1][1]] > 0:
                self_end.append(1)
            else:
                self_end.append(0)
            edge_len = [np.count_nonzero(npath_map1),
                        np.count_nonzero(npath_map2)]
            sorted_end_pts = [xx[0] for xx in sorted(
                zip(ravel_end, self_end, edge_len, [disp_diff1, disp_diff2]),
                key=lambda x: (x[1], x[2]),
                reverse=True
            )]
            re_npath_map1, re_fpath_map1 = (npath_map1 != -1).astype(
                np.uint8
            ), (fpath_map1 != -1).astype(np.uint8)
            re_npath_map2, re_fpath_map2 = (npath_map2 != -1).astype(
                np.uint8
            ), (fpath_map2 != -1).astype(np.uint8)
            if np.count_nonzero(re_npath_map1 * re_npath_map2 * mask) / \
                (np.count_nonzero(
                    (re_npath_map1 + re_npath_map2) * mask
                ) + 1e-6) > 0.5 \
                and np.count_nonzero(re_fpath_map1 * re_fpath_map2 * mask) / \
                (np.count_nonzero(
                    (re_fpath_map1 + re_fpath_map2) * mask
                ) + 1e-6) > 0.5 \
                and tmp_disp_diff[0] != -1 and tmp_disp_diff[1] != -1:
                my_fpath_map, my_npath_map, npath, fpath = \
                    plan_path_e2e(
                        mesh,
                        cc,
                        sorted_end_pts,
                        global_mesh,
                        input_edge,
                        mask,
                        inpaint_id,
                        npath_map=None,
                        fpath_map=None
                    )
                npath_map[my_npath_map != -1] = my_npath_map[my_npath_map != -1]
                fpath_map[my_fpath_map != -1] = my_fpath_map[my_fpath_map != -1]
                if len(fpath) > 0:
                    edge_id = global_mesh.nodes[[*sorted_end_pts][0]]['edge_id']
                    fpaths[edge_id] = fpath
                    npaths[edge_id] = npath
                invalid_edge_ids.append(edge_id)
            else:
                if tmp_disp_diff[0] != -1:
                    ratio_a = tmp_disp_diff[0] / (np.sum(tmp_disp_diff) + 1e-8)
                else:
                    ratio_a = 0
                if tmp_disp_diff[1] != -1:
                    ratio_b = tmp_disp_diff[1] / (np.sum(tmp_disp_diff) + 1e-8)
                else:
                    ratio_b = 0
                npath_len = len(tmp_npath)
                if npath_len > args.depth_edge_dilate_2 * 2:
                    npath_len = npath_len - (args.depth_edge_dilate_2 * 1)
                tmp_npath_a = tmp_npath[:int(np.floor(npath_len * ratio_a))]
                tmp_npath_b = tmp_npath[::-1][
                              :int(np.floor(npath_len * ratio_b))]
                tmp_merge = []
                if len(tmp_npath_a) > 0 and sorted_end_pts[0][0] == \
                    tmp_npath_a[0][0] and sorted_end_pts[0][1] == \
                    tmp_npath_a[0][1]:
                    if len(tmp_npath_a) > 0 and mask[
                        tmp_npath_a[-1][0], tmp_npath_a[-1][1]] > 0:
                        tmp_merge.append([sorted_end_pts[:1], tmp_npath_a])
                    if len(tmp_npath_b) > 0 and mask[
                        tmp_npath_b[-1][0], tmp_npath_b[-1][1]] > 0:
                        tmp_merge.append([sorted_end_pts[1:2], tmp_npath_b])
                elif len(tmp_npath_b) > 0 and sorted_end_pts[0][0] == \
                    tmp_npath_b[0][0] and sorted_end_pts[0][1] == \
                    tmp_npath_b[0][1]:
                    if len(tmp_npath_b) > 0 and mask[
                        tmp_npath_b[-1][0], tmp_npath_b[-1][1]] > 0:
                        tmp_merge.append([sorted_end_pts[:1], tmp_npath_b])
                    if len(tmp_npath_a) > 0 and mask[
                        tmp_npath_a[-1][0], tmp_npath_a[-1][1]] > 0:
                        tmp_merge.append([sorted_end_pts[1:2], tmp_npath_a])
                for tmp_idx in range(len(tmp_merge)):
                    if len(tmp_merge[tmp_idx][1]) == 0:
                        continue
                    end_pts.append(tmp_merge[tmp_idx][0])
                    ccs.append(set(tmp_merge[tmp_idx][1]))
        if len(end_pt) == 1:
            sub_mesh = mesh.subgraph(list(cc)).copy()
            pnodes = netx.periphery(sub_mesh)
            if len(end_pt) == 1:
                ends = [*end_pt]
            elif len(sorted_end_pt) == 1:
                ends = [*sorted_end_pt]
            else:
                pass
            try:
                edge_id = global_mesh.nodes[ends[0]]['edge_id']
            except:
                pass
            pnodes = sorted(
                pnodes,
                key=lambda x: np.hypot(
                    (x[0] - ends[0][0]),
                    (x[1] - ends[0][1])
                ),
                reverse=True
            )[0]
            npath = [*netx.shortest_path(
                sub_mesh,
                (ends[0][0], ends[0][1]),
                pnodes,
                weight='length'
            )]
            for np_node in npath:
                npath_map[np_node[0], np_node[1]] = edge_id
            fpath = []
            if global_mesh.nodes[ends[0]].get('far') is None:
                print("None far")
            else:
                fnodes = global_mesh.nodes[ends[0]].get('far')
                dmask = mask + 0
                did = 0
                while True:
                    did += 1
                    dmask = cv2.dilate(dmask, np.ones((3, 3)), iterations=1)
                    if did > 3:
                        break
                    ffnode = [fnode for fnode in fnodes if (
                        dmask[fnode[0], fnode[1]] > 0 and mask[
                        fnode[0], fnode[1]] == 0 and \
                        global_mesh.nodes[fnode].get(
                            'inpaint_id'
                        ) != inpaint_id + 1)]
                    if len(ffnode) > 0:
                        fnode = ffnode[0]
                        break
                if len(ffnode) == 0:
                    continue
                fpath.append((fnode[0], fnode[1]))
                barrel_dir = np.array(
                    [[1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1],
                     [0, -1], [1, -1]]
                )
                n2f_dir = (
                    int(fnode[0] - npath[0][0]), int(fnode[1] - npath[0][1]))
                while True:
                    if barrel_dir[0, 0] == n2f_dir[0] and barrel_dir[0, 1] == \
                        n2f_dir[1]:
                        n2f_barrel = barrel_dir.copy()
                        break
                    barrel_dir = np.roll(barrel_dir, 1, axis=0)
                for step in range(0, len(npath)):
                    if step == 0:
                        continue
                    elif step == 1:
                        next_dir = (npath[step][0] - npath[step - 1][0],
                                    npath[step][1] - npath[step - 1][1])
                        while True:
                            if barrel_dir[0, 0] == next_dir[0] and barrel_dir[
                                0, 1] == next_dir[1]:
                                next_barrel = barrel_dir.copy()
                                break
                            barrel_dir = np.roll(barrel_dir, 1, axis=0)
                        barrel_pair = np.stack(
                            (n2f_barrel, next_barrel),
                            axis=0
                        )
                        n2f_dir = (barrel_pair[0, 0, 0], barrel_pair[0, 0, 1])
                    elif step > 1:
                        next_dir = (npath[step][0] - npath[step - 1][0],
                                    npath[step][1] - npath[step - 1][1])
                        while True:
                            if barrel_pair[1, 0, 0] == next_dir[0] and \
                                barrel_pair[1, 0, 1] == next_dir[1]:
                                next_barrel = barrel_pair.copy()
                                break
                            barrel_pair = np.roll(barrel_pair, 1, axis=1)
                        n2f_dir = (barrel_pair[0, 0, 0], barrel_pair[0, 0, 1])
                    new_locs = []
                    if abs(n2f_dir[0]) == 1:
                        new_locs.append(
                            (npath[step][0] + n2f_dir[0], npath[step][1])
                        )
                    if abs(n2f_dir[1]) == 1:
                        new_locs.append(
                            (npath[step][0], npath[step][1] + n2f_dir[1])
                        )
                    if len(new_locs) > 1:
                        new_locs = sorted(
                            new_locs,
                            key=lambda xx: np.hypot(
                                (xx[0] - fpath[-1][0]),
                                (xx[1] - fpath[-1][1])
                            )
                        )
                    break_flag = False
                    for new_loc in new_locs:
                        new_loc_nes = [xx for xx in
                                       [(new_loc[0] + 1, new_loc[1]),
                                        (new_loc[0] - 1, new_loc[1]),
                                        (new_loc[0], new_loc[1] + 1),
                                        (new_loc[0], new_loc[1] - 1)] \
                                       if
                                       xx[0] >= 0 and xx[0] < fpath_map.shape[
                                           0] and xx[1] >= 0 and xx[1] <
                                       fpath_map.shape[1]]
                        if np.all(
                            [(fpath_map[nlne[0], nlne[1]] == -1) for nlne in
                             new_loc_nes]
                        ) != True:
                            break
                        if npath_map[new_loc[0], new_loc[1]] != -1:
                            if npath_map[new_loc[0], new_loc[1]] != edge_id:
                                break_flag = True
                                break
                            else:
                                continue
                        if valid_map[new_loc[0], new_loc[1]] == 0:
                            break_flag = True
                            break
                        fpath.append(new_loc)
                    if break_flag is True:
                        break
                if step != len(npath) - 1:
                    for xx in npath[step:]:
                        if npath_map[xx[0], xx[1]] == edge_id:
                            npath_map[xx[0], xx[1]] = -1
                    npath = npath[:step]
            if len(fpath) > 0:
                for fp_node in fpath:
                    fpath_map[fp_node[0], fp_node[1]] = edge_id
                fpaths[edge_id] = fpath
                npaths[edge_id] = npath
        fpath_map[valid_near_edge != 0] = -1
        if len(fpath) > 0:
            iter_fpath = copy.deepcopy(fpaths[edge_id])
        for node in iter_fpath:
            if valid_near_edge[node[0], node[1]] != 0:
                fpaths[edge_id].remove(node)

    return fpath_map, npath_map, False, npaths, fpaths, invalid_edge_ids


def plan_path_e2e(
    mesh,
    cc,
    end_pts,
    global_mesh,
    input_edge,
    mask,
    inpaint_id,
    npath_map=None,
    fpath_map=None
):
    my_npath_map = np.zeros_like(input_edge) - 1
    my_fpath_map = np.zeros_like(input_edge) - 1
    sub_mesh = mesh.subgraph(list(cc)).copy()
    ends_1, ends_2 = end_pts[0], end_pts[1]
    edge_id = global_mesh.nodes[ends_1]['edge_id']
    npath = [*netx.shortest_path(
        sub_mesh,
        (ends_1[0], ends_1[1]),
        (ends_2[0], ends_2[1]),
        weight='length'
    )]
    for np_node in npath:
        my_npath_map[np_node[0], np_node[1]] = edge_id
    fpath = []
    if global_mesh.nodes[ends_1].get('far') is None:
        print("None far")
    else:
        fnodes = global_mesh.nodes[ends_1].get('far')
        dmask = mask + 0
        while True:
            dmask = cv2.dilate(dmask, np.ones((3, 3)), iterations=1)
            ffnode = [fnode for fnode in fnodes if (
                dmask[fnode[0], fnode[1]] > 0 and mask[
                fnode[0], fnode[1]] == 0 and \
                global_mesh.nodes[fnode].get(
                    'inpaint_id'
                ) != inpaint_id + 1)]
            if len(ffnode) > 0:
                fnode = ffnode[0]
                break
        e_fnodes = global_mesh.nodes[ends_2].get('far')
        dmask = mask + 0
        while True:
            dmask = cv2.dilate(dmask, np.ones((3, 3)), iterations=1)
            e_ffnode = [e_fnode for e_fnode in e_fnodes if (
                dmask[e_fnode[0], e_fnode[1]] > 0 and mask[
                e_fnode[0], e_fnode[1]] == 0 and \
                global_mesh.nodes[e_fnode].get(
                    'inpaint_id'
                ) != inpaint_id + 1)]
            if len(e_ffnode) > 0:
                e_fnode = e_ffnode[0]
                break
        fpath.append((fnode[0], fnode[1]))
        if len(e_ffnode) == 0 or len(ffnode) == 0:
            return my_npath_map, my_fpath_map, [], []
        barrel_dir = np.array(
            [[1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1], [0, -1],
             [1, -1]]
        )
        n2f_dir = (int(fnode[0] - npath[0][0]), int(fnode[1] - npath[0][1]))
        while True:
            if barrel_dir[0, 0] == n2f_dir[0] and barrel_dir[0, 1] == n2f_dir[
                1]:
                n2f_barrel = barrel_dir.copy()
                break
            barrel_dir = np.roll(barrel_dir, 1, axis=0)
        for step in range(0, len(npath)):
            if step == 0:
                continue
            elif step == 1:
                next_dir = (npath[step][0] - npath[step - 1][0],
                            npath[step][1] - npath[step - 1][1])
                while True:
                    if barrel_dir[0, 0] == next_dir[0] and barrel_dir[0, 1] == \
                        next_dir[1]:
                        next_barrel = barrel_dir.copy()
                        break
                    barrel_dir = np.roll(barrel_dir, 1, axis=0)
                barrel_pair = np.stack((n2f_barrel, next_barrel), axis=0)
                n2f_dir = (barrel_pair[0, 0, 0], barrel_pair[0, 0, 1])
            elif step > 1:
                next_dir = (npath[step][0] - npath[step - 1][0],
                            npath[step][1] - npath[step - 1][1])
                while True:
                    if barrel_pair[1, 0, 0] == next_dir[0] and barrel_pair[
                        1, 0, 1] == next_dir[1]:
                        next_barrel = barrel_pair.copy()
                        break
                    barrel_pair = np.roll(barrel_pair, 1, axis=1)
                n2f_dir = (barrel_pair[0, 0, 0], barrel_pair[0, 0, 1])
            new_locs = []
            if abs(n2f_dir[0]) == 1:
                new_locs.append((npath[step][0] + n2f_dir[0], npath[step][1]))
            if abs(n2f_dir[1]) == 1:
                new_locs.append((npath[step][0], npath[step][1] + n2f_dir[1]))
            if len(new_locs) > 1:
                new_locs = sorted(
                    new_locs,
                    key=lambda xx: np.hypot(
                        (xx[0] - fpath[-1][0]),
                        (xx[1] - fpath[-1][1])
                    )
                )
            break_flag = False
            for new_loc in new_locs:
                new_loc_nes = [xx for xx in [(new_loc[0] + 1, new_loc[1]),
                                             (new_loc[0] - 1, new_loc[1]),
                                             (new_loc[0], new_loc[1] + 1),
                                             (new_loc[0], new_loc[1] - 1)] \
                               if
                               xx[0] >= 0 and xx[0] < my_fpath_map.shape[0] and
                               xx[1] >= 0 and xx[1] < my_fpath_map.shape[1]]
                if fpath_map is not None and np.sum(
                    [fpath_map[nlne[0], nlne[1]] for nlne in new_loc_nes]
                ) != 0:
                    break_flag = True
                    break
                if my_npath_map[new_loc[0], new_loc[1]] != -1:
                    continue
                if npath_map is not None and npath_map[
                    new_loc[0], new_loc[1]] != edge_id:
                    break_flag = True
                    break
                fpath.append(new_loc)
            if break_flag is True:
                break
        if (e_fnode[0], e_fnode[1]) not in fpath:
            fpath.append((e_fnode[0], e_fnode[1]))
        if step != len(npath) - 1:
            for xx in npath[step:]:
                if my_npath_map[xx[0], xx[1]] == edge_id:
                    my_npath_map[xx[0], xx[1]] = -1
            npath = npath[:step]
        if len(fpath) > 0:
            for fp_node in fpath:
                my_fpath_map[fp_node[0], fp_node[1]] = edge_id

    return my_fpath_map, my_npath_map, npath, fpath


def plan_path(
    mesh,
    info_on_pix,
    cc,
    end_pt,
    global_mesh,
    input_edge,
    mask,
    valid_map,
    inpaint_id,
    npath_map=None,
    fpath_map=None,
    npath=None
):
    my_npath_map = np.zeros_like(input_edge) - 1
    my_fpath_map = np.zeros_like(input_edge) - 1
    sub_mesh = mesh.subgraph(list(cc)).copy()
    pnodes = netx.periphery(sub_mesh)
    ends = [*end_pt]
    edge_id = global_mesh.nodes[ends[0]]['edge_id']
    pnodes = sorted(
        pnodes,
        key=lambda x: np.hypot((x[0] - ends[0][0]), (x[1] - ends[0][1])),
        reverse=True
    )[0]
    if npath is None:
        npath = [*netx.shortest_path(
            sub_mesh,
            (ends[0][0], ends[0][1]),
            pnodes,
            weight='length'
        )]
    else:
        if (ends[0][0], ends[0][1]) == npath[0]:
            npath = npath
        elif (ends[0][0], ends[0][1]) == npath[-1]:
            npath = npath[::-1]
        else:
            pass
    for np_node in npath:
        my_npath_map[np_node[0], np_node[1]] = edge_id
    fpath = []
    if global_mesh.nodes[ends[0]].get('far') is None:
        print("None far")
    else:
        fnodes = global_mesh.nodes[ends[0]].get('far')
        dmask = mask + 0
        did = 0
        while True:
            did += 1
            if did > 3:
                return my_fpath_map, my_npath_map, -1
            dmask = cv2.dilate(dmask, np.ones((3, 3)), iterations=1)
            ffnode = [fnode for fnode in fnodes if (
                dmask[fnode[0], fnode[1]] > 0 and mask[
                fnode[0], fnode[1]] == 0 and \
                global_mesh.nodes[fnode].get(
                    'inpaint_id'
                ) != inpaint_id + 1)]
            if len(ffnode) > 0:
                fnode = ffnode[0]
                break

        fpath.append((fnode[0], fnode[1]))
        disp_diff = 0.
        for n_loc in npath:
            if mask[n_loc[0], n_loc[1]] != 0:
                disp_diff = abs(
                    abs(
                        1. / info_on_pix[(n_loc[0], n_loc[1])][0]['depth']
                    ) - abs(1. / ends[0][2])
                )
                break
        barrel_dir = np.array(
            [[1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1], [0, -1],
             [1, -1]]
        )
        n2f_dir = (int(fnode[0] - npath[0][0]), int(fnode[1] - npath[0][1]))
        while True:
            if barrel_dir[0, 0] == n2f_dir[0] and barrel_dir[0, 1] == n2f_dir[
                1]:
                n2f_barrel = barrel_dir.copy()
                break
            barrel_dir = np.roll(barrel_dir, 1, axis=0)
        for step in range(0, len(npath)):
            if step == 0:
                continue
            elif step == 1:
                next_dir = (npath[step][0] - npath[step - 1][0],
                            npath[step][1] - npath[step - 1][1])
                while True:
                    if barrel_dir[0, 0] == next_dir[0] and barrel_dir[0, 1] == \
                        next_dir[1]:
                        next_barrel = barrel_dir.copy()
                        break
                    barrel_dir = np.roll(barrel_dir, 1, axis=0)
                barrel_pair = np.stack((n2f_barrel, next_barrel), axis=0)
                n2f_dir = (barrel_pair[0, 0, 0], barrel_pair[0, 0, 1])
            elif step > 1:
                next_dir = (npath[step][0] - npath[step - 1][0],
                            npath[step][1] - npath[step - 1][1])
                while True:
                    if barrel_pair[1, 0, 0] == next_dir[0] and barrel_pair[
                        1, 0, 1] == next_dir[1]:
                        next_barrel = barrel_pair.copy()
                        break
                    barrel_pair = np.roll(barrel_pair, 1, axis=1)
                n2f_dir = (barrel_pair[0, 0, 0], barrel_pair[0, 0, 1])
            new_locs = []
            if abs(n2f_dir[0]) == 1:
                new_locs.append((npath[step][0] + n2f_dir[0], npath[step][1]))
            if abs(n2f_dir[1]) == 1:
                new_locs.append((npath[step][0], npath[step][1] + n2f_dir[1]))
            if len(new_locs) > 1:
                new_locs = sorted(
                    new_locs,
                    key=lambda xx: np.hypot(
                        (xx[0] - fpath[-1][0]),
                        (xx[1] - fpath[-1][1])
                    )
                )
            break_flag = False
            for new_loc in new_locs:
                new_loc_nes = [xx for xx in [(new_loc[0] + 1, new_loc[1]),
                                             (new_loc[0] - 1, new_loc[1]),
                                             (new_loc[0], new_loc[1] + 1),
                                             (new_loc[0], new_loc[1] - 1)] \
                               if
                               xx[0] >= 0 and xx[0] < my_fpath_map.shape[0] and
                               xx[1] >= 0 and xx[1] < my_fpath_map.shape[1]]
                if fpath_map is not None and np.all(
                    [(fpath_map[nlne[0], nlne[1]] == -1) for nlne in
                     new_loc_nes]
                ) != True:
                    break_flag = True
                    break
                if np.all(
                    [(my_fpath_map[nlne[0], nlne[1]] == -1) for nlne in
                     new_loc_nes]
                ) != True:
                    break_flag = True
                    break
                if my_npath_map[new_loc[0], new_loc[1]] != -1:
                    continue
                if npath_map is not None and npath_map[
                    new_loc[0], new_loc[1]] != edge_id:
                    break_flag = True
                    break
                if valid_map[new_loc[0], new_loc[1]] == 0:
                    break_flag = True
                    break
                fpath.append(new_loc)
            if break_flag is True:
                break
        if step != len(npath) - 1:
            for xx in npath[step:]:
                if my_npath_map[xx[0], xx[1]] == edge_id:
                    my_npath_map[xx[0], xx[1]] = -1
            npath = npath[:step]
        if len(fpath) > 0:
            for fp_node in fpath:
                my_fpath_map[fp_node[0], fp_node[1]] = edge_id

    return my_fpath_map, my_npath_map, disp_diff


def refresh_node(old_node, old_feat, new_node, new_feat, mesh, stime=False):
    mesh.add_node(new_node)
    mesh.nodes[new_node].update(new_feat)
    mesh.nodes[new_node].update(old_feat)
    for ne in mesh.neighbors(old_node):
        mesh.add_edge(new_node, ne)
    if mesh.nodes[new_node].get('far') is not None:
        tmp_far_nodes = mesh.nodes[new_node]['far']
        for far_node in tmp_far_nodes:
            if mesh.has_node(far_node) is False:
                mesh.nodes[new_node]['far'].remove(far_node)
                continue
            if mesh.nodes[far_node].get('near') is not None:
                for idx in range(len(mesh.nodes[far_node].get('near'))):
                    if mesh.nodes[far_node]['near'][idx][0] == new_node[0] and \
                        mesh.nodes[far_node]['near'][idx][1] == new_node[1]:
                        if len(mesh.nodes[far_node]['near'][idx]) == len(
                            old_node
                        ):
                            mesh.nodes[far_node]['near'][idx] = new_node
    if mesh.nodes[new_node].get('near') is not None:
        tmp_near_nodes = mesh.nodes[new_node]['near']
        for near_node in tmp_near_nodes:
            if mesh.has_node(near_node) is False:
                mesh.nodes[new_node]['near'].remove(near_node)
                continue
            if mesh.nodes[near_node].get('far') is not None:
                for idx in range(len(mesh.nodes[near_node].get('far'))):
                    if mesh.nodes[near_node]['far'][idx][0] == new_node[0] and \
                        mesh.nodes[near_node]['far'][idx][1] == new_node[1]:
                        if len(mesh.nodes[near_node]['far'][idx]) == len(
                            old_node
                        ):
                            mesh.nodes[near_node]['far'][idx] = new_node
    if new_node != old_node:
        mesh.remove_node(old_node)
    if stime is False:
        return mesh
    else:
        return mesh, None, None


def create_placeholder(
    context,
    mask,
    depth,
    fpath_map,
    npath_map,
    mesh,
    inpaint_id,
    edge_ccs,
    extend_edge_cc,
    all_edge_maps,
    self_edge_id
):
    add_node_time = 0
    add_edge_time = 0
    add_far_near_time = 0
    valid_area = context + mask
    H, W = mesh.graph['H'], mesh.graph['W']
    edge_cc = edge_ccs[self_edge_id]
    num_com = len(edge_cc) + len(extend_edge_cc)
    hxs, hys = np.where(mask > 0)
    for hx, hy in zip(hxs, hys):
        mesh.add_node((hx, hy), inpaint_id=inpaint_id + 1, num_context=num_com)
    for hx, hy in zip(hxs, hys):
        four_nes = [(x, y) for x, y in
                    [(hx + 1, hy), (hx - 1, hy), (hx, hy + 1), (hx, hy - 1)] if \
                    0 <= x < mesh.graph['H'] and 0 <= y < mesh.graph['W'] and
                    valid_area[x, y] != 0]
        for ne in four_nes:
            if mask[ne[0], ne[1]] != 0:
                if not mesh.has_edge((hx, hy), ne):
                    mesh.add_edge((hx, hy), ne)
            elif depth[ne[0], ne[1]] != 0:
                if mesh.has_node((ne[0], ne[1], depth[ne[0], ne[1]])) and \
                    not mesh.has_edge(
                        (hx, hy),
                        (ne[0], ne[1], depth[ne[0], ne[1]])
                    ):
                    mesh.add_edge((hx, hy), (ne[0], ne[1], depth[ne[0], ne[1]]))
                else:
                    print("Undefined context node.")
                    pass
    near_ids = np.unique(npath_map)
    if near_ids[0] == -1:
        near_ids = near_ids[1:]
    for near_id in near_ids:
        hxs, hys = np.where((fpath_map == near_id) & (mask > 0))
        if hxs.shape[0] > 0:
            mesh.graph['max_edge_id'] = mesh.graph['max_edge_id'] + 1
        else:
            break
        for hx, hy in zip(hxs, hys):
            mesh.nodes[(hx, hy)]['edge_id'] = int(
                round(mesh.graph['max_edge_id'])
            )
            four_nes = [(x, y) for x, y in
                        [(hx + 1, hy), (hx - 1, hy), (hx, hy + 1), (hx, hy - 1)]
                        if \
                        x < mesh.graph['H'] and x >= 0 and y < mesh.graph[
                            'W'] and y >= 0 and npath_map[x, y] == near_id]
            for xx in four_nes:
                xx_n = copy.deepcopy(xx)
                if not mesh.has_node(xx_n):
                    if mesh.has_node(
                        (xx_n[0], xx_n[1], depth[xx_n[0], xx_n[1]])
                    ):
                        xx_n = (xx_n[0], xx_n[1], depth[xx_n[0], xx_n[1]])
                if mesh.has_edge((hx, hy), xx_n):
                    # pass
                    mesh.remove_edge((hx, hy), xx_n)
                if mesh.nodes[(hx, hy)].get('near') is None:
                    mesh.nodes[(hx, hy)]['near'] = []
                mesh.nodes[(hx, hy)]['near'].append(xx_n)
        connect_point_exception = set()
        hxs, hys = np.where((npath_map == near_id) & (all_edge_maps > -1))
        for hx, hy in zip(hxs, hys):
            unknown_id = int(round(all_edge_maps[hx, hy]))
            if unknown_id != near_id and unknown_id != self_edge_id:
                unknown_node = set(
                    [xx for xx in edge_ccs[unknown_id] if
                     xx[0] == hx and xx[1] == hy]
                )
                connect_point_exception |= unknown_node
        hxs, hys = np.where((npath_map == near_id) & (mask > 0))
        if hxs.shape[0] > 0:
            mesh.graph['max_edge_id'] = mesh.graph['max_edge_id'] + 1
        else:
            break
        for hx, hy in zip(hxs, hys):
            mesh.nodes[(hx, hy)]['edge_id'] = int(
                round(mesh.graph['max_edge_id'])
            )
            mesh.nodes[(hx, hy)]['connect_point_id'] = int(round(near_id))
            mesh.nodes[(hx, hy)][
                'connect_point_exception'] = connect_point_exception
            four_nes = [(x, y) for x, y in
                        [(hx + 1, hy), (hx - 1, hy), (hx, hy + 1), (hx, hy - 1)]
                        if \
                        x < mesh.graph['H'] and x >= 0 and y < mesh.graph[
                            'W'] and y >= 0 and fpath_map[x, y] == near_id]
            for xx in four_nes:
                xx_n = copy.deepcopy(xx)
                if not mesh.has_node(xx_n):
                    if mesh.has_node(
                        (xx_n[0], xx_n[1], depth[xx_n[0], xx_n[1]])
                    ):
                        xx_n = (xx_n[0], xx_n[1], depth[xx_n[0], xx_n[1]])
                if mesh.has_edge((hx, hy), xx_n):
                    mesh.remove_edge((hx, hy), xx_n)
                if mesh.nodes[(hx, hy)].get('far') is None:
                    mesh.nodes[(hx, hy)]['far'] = []
                mesh.nodes[(hx, hy)]['far'].append(xx_n)

    return mesh, add_node_time, add_edge_time, add_far_near_time


def get_MiDaS_sample(args, aft_certain=None):
    image_file = args.input_file
    depth_folder = args.depth_folder
    specific = args.specific

    image_folder = os.path.dirname(image_file)

    seq_dir = os.path.splitext(os.path.basename(image_file))[0]
    generic_pose = np.eye(4)

    tgts_pose = generic_pose * 1.
    # @todo NB: this doesn't do any rotation, only translation
    # @see mesh.output_3d_photo
    tgts_pose[:3, -1] = np.array([
        args.x_shift,
        args.y_shift,
        args.z_shift
    ])

    aft_flag = True
    if aft_certain is not None and len(aft_certain) > 0:
        aft_flag = False

    if specific is not None and len(specific) > 0:
        if specific != seq_dir:
            return

    if aft_certain is not None and len(aft_certain) > 0:
        if aft_certain == seq_dir:
            aft_flag = True
        if aft_flag is False:
            return

    sample = {
        'depth_fi': os.path.join(
            depth_folder,
            seq_dir + args.depth_format
        ),
        'ref_img_fi': os.path.join(
            image_folder,
            seq_dir + args.img_format
        )
    }
    height, width = imageio.imread(sample['ref_img_fi']).shape[:2]
    sample['int_mtx'] = np.array(
        [
            [max(height, width), 0, width // 2],
            [0, max(height, width), height // 2],
            [0, 0, 1]
        ]
    ).astype(np.float32)
    if sample['int_mtx'].max() > 1:
        sample['int_mtx'][0, :] = sample['int_mtx'][0, :] / float(width)
        sample['int_mtx'][1, :] = sample['int_mtx'][1, :] / float(height)

    sample['ref_pose'] = np.eye(4)
    sample['tgts_pose'] = tgts_pose
    sample['video_postfix'] = args.video_postfix
    sample['tgt_name'] = os.path.splitext(
        os.path.basename(sample['depth_fi'])
    )[0]

    return sample


def get_valid_size(imap):
    x_max = np.where(imap.sum(1).squeeze() > 0)[0].max() + 1
    x_min = np.where(imap.sum(1).squeeze() > 0)[0].min()
    y_max = np.where(imap.sum(0).squeeze() > 0)[0].max() + 1
    y_min = np.where(imap.sum(0).squeeze() > 0)[0].min()
    size_dict = {'x_max': x_max, 'y_max': y_max, 'x_min': x_min, 'y_min': y_min}

    return size_dict


def dilate_valid_size(isize_dict, imap, dilate=[0, 0]):
    osize_dict = copy.deepcopy(isize_dict)
    osize_dict['x_min'] = max(0, osize_dict['x_min'] - dilate[0])
    osize_dict['x_max'] = min(imap.shape[0], osize_dict['x_max'] + dilate[0])
    osize_dict['y_min'] = max(0, osize_dict['y_min'] - dilate[0])
    osize_dict['y_max'] = min(imap.shape[1], osize_dict['y_max'] + dilate[1])

    return osize_dict


def crop_maps_by_size(size, *imaps):
    omaps = []
    for imap in imaps:
        omaps.append(
            imap[size['x_min']:size['x_max'],
            size['y_min']:size['y_max']].copy()
        )

    return omaps


def smooth_cntsyn_gap(
    init_depth_map,
    mask_region,
    context_region,
    init_mask_region=None
):
    if init_mask_region is not None:
        curr_mask_region = init_mask_region * 1
    else:
        curr_mask_region = mask_region * 0
    depth_map = init_depth_map.copy()
    for _ in range(2):
        cm_mask = context_region + curr_mask_region
        depth_s1 = np.roll(depth_map, 1, 0)
        depth_s2 = np.roll(depth_map, -1, 0)
        depth_s3 = np.roll(depth_map, 1, 1)
        depth_s4 = np.roll(depth_map, -1, 1)
        mask_s1 = np.roll(cm_mask, 1, 0)
        mask_s2 = np.roll(cm_mask, -1, 0)
        mask_s3 = np.roll(cm_mask, 1, 1)
        mask_s4 = np.roll(cm_mask, -1, 1)
        fluxin_depths = (
                            depth_s1 * mask_s1 + depth_s2 * mask_s2 + depth_s3 * mask_s3 + depth_s4 * mask_s4) / \
                        ((mask_s1 + mask_s2 + mask_s3 + mask_s4) + 1e-6)
        fluxin_mask = (fluxin_depths != 0) * mask_region
        init_mask = (fluxin_mask * (curr_mask_region >= 0).astype(
            np.float32
        ) > 0).astype(np.uint8)
        depth_map[init_mask > 0] = fluxin_depths[init_mask > 0]
        if init_mask.shape[-1] > curr_mask_region.shape[-1]:
            curr_mask_region[init_mask.sum(-1, keepdims=True) > 0] = 1
        else:
            curr_mask_region[init_mask > 0] = 1
        depth_map[fluxin_mask > 0] = fluxin_depths[fluxin_mask > 0]

    return depth_map


def read_MiDaS_depth(disp_fi, disp_rescale=10., h=None, w=None):
    if 'npy' in os.path.splitext(disp_fi)[-1]:
        disp = np.load(disp_fi)
    else:
        disp = imageio.imread(disp_fi).astype(np.float32)
    disp = disp - disp.min()
    disp = cv2.blur(disp / disp.max(), ksize=(3, 3)) * disp.max()
    disp = (disp / disp.max()) * disp_rescale
    if h is not None and w is not None:
        disp = resize(disp / disp.max(), (h, w), order=1) * disp.max()
    depth = 1. / np.maximum(disp, 0.05)

    return depth


def follow_image_aspect_ratio(depth, image):
    H, W = image.shape[:2]
    image_aspect_ratio = H / W
    dH, dW = depth.shape[:2]
    depth_aspect_ratio = dH / dW
    if depth_aspect_ratio > image_aspect_ratio:
        resize_H = dH
        resize_W = dH / image_aspect_ratio
    else:
        resize_W = dW
        resize_H = dW * image_aspect_ratio
    depth = resize(
        depth / depth.max(),
        (int(resize_H),
         int(resize_W)),
        order=0
    ) * depth.max()

    return depth


def depth_resize(depth, origin_size, image_size):
    if origin_size[0] is not 0:
        max_depth = depth.max()
        depth = depth / max_depth
        depth = resize(depth, origin_size, order=1, mode='edge')
        depth = depth * max_depth
    else:
        max_depth = depth.max()
        depth = depth / max_depth
        depth = resize(depth, image_size, order=1, mode='edge')
        depth = depth * max_depth

    return depth


def require_depth_edge(context_edge, mask):
    dilate_mask = cv2.dilate(
        mask,
        np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]]).astype(np.uint8),
        iterations=1
    )
    if (dilate_mask * context_edge).max() == 0:
        return False
    else:
        return True


def refine_color_around_edge(mesh, info_on_pix, edge_ccs):
    H, W = mesh.graph['H'], mesh.graph['W']
    tmp_edge_ccs = copy.deepcopy(edge_ccs)
    for edge_id, edge_cc in enumerate(edge_ccs):
        if len(edge_cc) == 0:
            continue
        near_maps = np.zeros((H, W)).astype(np.bool)
        far_maps = np.zeros((H, W)).astype(np.bool)
        tmp_far_nodes = set()
        far_nodes = set()
        near_nodes = set()
        end_nodes = set()
        for i in range(5):
            if i == 0:
                for edge_node in edge_cc:
                    if mesh.nodes[edge_node].get(
                        'depth_edge_dilate_2_color_flag'
                    ) is not True:
                        break
                    if mesh.nodes[edge_node].get('inpaint_id') == 1:
                        near_nodes.add(edge_node)
                        tmp_node = mesh.nodes[edge_node].get('far')
                        tmp_node = set(
                            tmp_node
                        ) if tmp_node is not None else set()
                        tmp_far_nodes |= tmp_node
                rmv_tmp_far_nodes = set()
                for far_node in tmp_far_nodes:
                    if not (
                        mesh.has_node(far_node) and mesh.nodes[far_node].get(
                        'inpaint_id'
                    ) == 1):
                        rmv_tmp_far_nodes.add(far_node)
                if len(tmp_far_nodes - rmv_tmp_far_nodes) == 0:
                    break
                else:
                    for near_node in near_nodes:
                        near_maps[near_node[0], near_node[1]] = True
                        mesh.nodes[near_node]['refine_rgbd'] = True
                        mesh.nodes[near_node]['backup_depth'] = near_node[2] \
                            if mesh.nodes[near_node].get(
                            'real_depth'
                        ) is None else mesh.nodes[near_node]['real_depth']
                        mesh.nodes[near_node]['backup_color'] = \
                            mesh.nodes[near_node]['color']
                for far_node in tmp_far_nodes:
                    if mesh.has_node(far_node) and mesh.nodes[far_node].get(
                        'inpaint_id'
                    ) == 1:
                        far_nodes.add(far_node)
                        far_maps[far_node[0], far_node[1]] = True
                        mesh.nodes[far_node]['refine_rgbd'] = True
                        mesh.nodes[far_node]['backup_depth'] = far_node[2] \
                            if mesh.nodes[far_node].get(
                            'real_depth'
                        ) is None else mesh.nodes[far_node]['real_depth']
                        mesh.nodes[far_node]['backup_color'] = \
                            mesh.nodes[far_node]['color']
                tmp_far_nodes = far_nodes
                tmp_near_nodes = near_nodes
            else:
                tmp_far_nodes = new_tmp_far_nodes
                tmp_near_nodes = new_tmp_near_nodes
                new_tmp_far_nodes = None
                new_tmp_near_nodes = None
            new_tmp_far_nodes = set()
            new_tmp_near_nodes = set()
            for node in tmp_near_nodes:
                for ne_node in mesh.neighbors(node):
                    if far_maps[ne_node[0], ne_node[1]] == False and \
                        near_maps[ne_node[0], ne_node[1]] == False:
                        if mesh.nodes[ne_node].get('inpaint_id') == 1:
                            new_tmp_near_nodes.add(ne_node)
                            near_maps[ne_node[0], ne_node[1]] = True
                            mesh.nodes[ne_node]['refine_rgbd'] = True
                            mesh.nodes[ne_node]['backup_depth'] = ne_node[2] \
                                if mesh.nodes[ne_node].get(
                                'real_depth'
                            ) is None else mesh.nodes[ne_node]['real_depth']
                            mesh.nodes[ne_node]['backup_color'] = \
                                mesh.nodes[ne_node]['color']
                        else:
                            mesh.nodes[ne_node]['backup_depth'] = ne_node[2] \
                                if mesh.nodes[ne_node].get(
                                'real_depth'
                            ) is None else mesh.nodes[ne_node]['real_depth']
                            mesh.nodes[ne_node]['backup_color'] = \
                                mesh.nodes[ne_node]['color']
                            end_nodes.add(node)
            near_nodes.update(new_tmp_near_nodes)
            for node in tmp_far_nodes:
                for ne_node in mesh.neighbors(node):
                    if far_maps[ne_node[0], ne_node[1]] == False and \
                        near_maps[ne_node[0], ne_node[1]] == False:
                        if mesh.nodes[ne_node].get('inpaint_id') == 1:
                            new_tmp_far_nodes.add(ne_node)
                            far_maps[ne_node[0], ne_node[1]] = True
                            mesh.nodes[ne_node]['refine_rgbd'] = True
                            mesh.nodes[ne_node]['backup_depth'] = ne_node[2] \
                                if mesh.nodes[ne_node].get(
                                'real_depth'
                            ) is None else mesh.nodes[ne_node]['real_depth']
                            mesh.nodes[ne_node]['backup_color'] = \
                                mesh.nodes[ne_node]['color']
                        else:
                            mesh.nodes[ne_node]['backup_depth'] = ne_node[2] \
                                if mesh.nodes[ne_node].get(
                                'real_depth'
                            ) is None else mesh.nodes[ne_node]['real_depth']
                            mesh.nodes[ne_node]['backup_color'] = \
                                mesh.nodes[ne_node]['color']
                            end_nodes.add(node)
            far_nodes.update(new_tmp_far_nodes)
        if len(far_nodes) == 0:
            tmp_edge_ccs[edge_id] = set()
            continue
        for node in new_tmp_far_nodes | new_tmp_near_nodes:
            for ne_node in mesh.neighbors(node):
                if far_maps[ne_node[0], ne_node[1]] == False and near_maps[
                    ne_node[0], ne_node[1]] == False:
                    end_nodes.add(node)
                    mesh.nodes[ne_node]['backup_depth'] = ne_node[2] \
                        if mesh.nodes[ne_node].get('real_depth') is None else \
                        mesh.nodes[ne_node]['real_depth']
                    mesh.nodes[ne_node]['backup_color'] = mesh.nodes[ne_node][
                        'color']
        tmp_end_nodes = end_nodes

        refine_nodes = near_nodes | far_nodes
        remain_refine_nodes = copy.deepcopy(refine_nodes)
        accum_idx = 0
        while len(remain_refine_nodes) > 0:
            accum_idx += 1
            if accum_idx > 100:
                break
            new_tmp_end_nodes = None
            new_tmp_end_nodes = set()
            survive_tmp_end_nodes = set()
            for node in tmp_end_nodes:
                re_depth, re_color, re_count = 0, np.array([0., 0., 0.]), 0
                for ne_node in mesh.neighbors(node):
                    if mesh.nodes[ne_node].get('refine_rgbd') is True:
                        if ne_node not in tmp_end_nodes:
                            new_tmp_end_nodes.add(ne_node)
                    else:
                        try:
                            re_depth += mesh.nodes[ne_node]['backup_depth']
                            re_color += mesh.nodes[ne_node][
                                'backup_color'].astype(np.float32)
                            re_count += 1.
                        except:
                            pass
                if re_count > 0:
                    re_depth = re_depth / re_count
                    re_color = re_color / re_count
                    mesh.nodes[node]['backup_depth'] = re_depth
                    mesh.nodes[node]['backup_color'] = re_color
                    mesh.nodes[node]['refine_rgbd'] = False
                else:
                    survive_tmp_end_nodes.add(node)
            for node in tmp_end_nodes - survive_tmp_end_nodes:
                if node in remain_refine_nodes:
                    remain_refine_nodes.remove(node)
            tmp_end_nodes = new_tmp_end_nodes

        for node in refine_nodes:
            if mesh.nodes[node].get('refine_rgbd') is not None:
                mesh.nodes[node].pop('refine_rgbd')
                mesh.nodes[node]['color'] = mesh.nodes[node]['backup_color']
                for info in info_on_pix[(node[0], node[1])]:
                    if info['depth'] == node[2]:
                        info['color'] = mesh.nodes[node]['backup_color']

    return mesh, info_on_pix


def refine_depth_around_edge(
    mask_depth,
    far_edge,
    uncleaned_far_edge,
    near_edge,
    mask,
    all_depth,
    args
):
    if isinstance(mask_depth, torch.Tensor):
        if mask_depth.is_cuda:
            mask_depth = mask_depth.cpu()
        mask_depth = mask_depth.data
        mask_depth = mask_depth.numpy()
    if isinstance(far_edge, torch.Tensor):
        if far_edge.is_cuda:
            far_edge = far_edge.cpu()
        far_edge = far_edge.data
        far_edge = far_edge.numpy()
    if isinstance(uncleaned_far_edge, torch.Tensor):
        if uncleaned_far_edge.is_cuda:
            uncleaned_far_edge = uncleaned_far_edge.cpu()
        uncleaned_far_edge = uncleaned_far_edge.data
        uncleaned_far_edge = uncleaned_far_edge.numpy()
    if isinstance(near_edge, torch.Tensor):
        if near_edge.is_cuda:
            near_edge = near_edge.cpu()
        near_edge = near_edge.data
        near_edge = near_edge.numpy()
    if isinstance(mask, torch.Tensor):
        if mask.is_cuda:
            mask = mask.cpu()
        mask = mask.data
        mask = mask.numpy()
    mask = mask.squeeze()
    uncleaned_far_edge = uncleaned_far_edge.squeeze()
    far_edge = far_edge.squeeze()
    near_edge = near_edge.squeeze()
    mask_depth = mask_depth.squeeze()
    dilate_far_edge = cv2.dilate(
        uncleaned_far_edge.astype(np.uint8),
        kernel=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]]).astype(np.uint8),
        iterations=1
    )
    near_edge[dilate_far_edge == 0] = 0
    dilate_near_edge = cv2.dilate(
        near_edge.astype(np.uint8),
        kernel=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]]).astype(np.uint8),
        iterations=1
    )
    far_edge[dilate_near_edge == 0] = 0
    init_far_edge = far_edge.copy()
    init_near_edge = near_edge.copy()
    for i in range(args.depth_edge_dilate_2):
        init_far_edge = cv2.dilate(
            init_far_edge,
            kernel=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]]).astype(np.uint8),
            iterations=1
        )
        init_far_edge[init_near_edge == 1] = 0
        init_near_edge = cv2.dilate(
            init_near_edge,
            kernel=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]]).astype(np.uint8),
            iterations=1
        )
        init_near_edge[init_far_edge == 1] = 0
    init_far_edge[mask == 0] = 0
    init_near_edge[mask == 0] = 0
    hole_far_edge = 1 - init_far_edge
    hole_near_edge = 1 - init_near_edge
    change = None
    while True:
        change = False
        hole_far_edge[init_near_edge == 1] = 0
        hole_near_edge[init_far_edge == 1] = 0
        far_pxs, far_pys = np.where(
            (hole_far_edge == 0) * (init_far_edge == 1) > 0
        )
        current_hole_far_edge = hole_far_edge.copy()
        for far_px, far_py in zip(far_pxs, far_pys):
            min_px = max(far_px - 1, 0)
            max_px = min(far_px + 2, mask.shape[0] - 1)
            min_py = max(far_py - 1, 0)
            max_py = min(far_py + 2, mask.shape[1] - 1)
            hole_far = current_hole_far_edge[min_px: max_px, min_py: max_py]
            tmp_mask = mask[min_px: max_px, min_py: max_py]
            all_depth_patch = all_depth[min_px: max_px, min_py: max_py] * 0
            all_depth_mask = (all_depth_patch != 0).astype(np.uint8)
            cross_element = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])[
                            min_px - (far_px - 1): max_px - (far_px - 1),
                            min_py - (far_py - 1): max_py - (far_py - 1)]
            combine_mask = (tmp_mask + all_depth_mask).clip(
                0,
                1
            ) * hole_far * cross_element
            tmp_patch = combine_mask * (mask_depth[min_px: max_px,
                                        min_py: max_py] + all_depth_patch)
            number = np.count_nonzero(tmp_patch)
            if number > 0:
                mask_depth[far_px, far_py] = np.sum(tmp_patch).astype(
                    np.float32
                ) / max(number, 1e-6)
                hole_far_edge[far_px, far_py] = 1
                change = True
        near_pxs, near_pys = np.where(
            (hole_near_edge == 0) * (init_near_edge == 1) > 0
        )
        current_hole_near_edge = hole_near_edge.copy()
        for near_px, near_py in zip(near_pxs, near_pys):
            min_px = max(near_px - 1, 0)
            max_px = min(near_px + 2, mask.shape[0] - 1)
            min_py = max(near_py - 1, 0)
            max_py = min(near_py + 2, mask.shape[1] - 1)
            hole_near = current_hole_near_edge[min_px: max_px, min_py: max_py]
            tmp_mask = mask[min_px: max_px, min_py: max_py]
            all_depth_patch = all_depth[min_px: max_px, min_py: max_py] * 0
            all_depth_mask = (all_depth_patch != 0).astype(np.uint8)
            cross_element = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])[
                            min_px - near_px + 1:max_px - near_px + 1,
                            min_py - near_py + 1:max_py - near_py + 1]
            combine_mask = (tmp_mask + all_depth_mask).clip(
                0,
                1
            ) * hole_near * cross_element
            tmp_patch = combine_mask * (mask_depth[min_px: max_px,
                                        min_py: max_py] + all_depth_patch)
            number = np.count_nonzero(tmp_patch)
            if number > 0:
                mask_depth[near_px, near_py] = np.sum(tmp_patch) / max(
                    number,
                    1e-6
                )
                hole_near_edge[near_px, near_py] = 1
                change = True
        if change is False:
            break

    return mask_depth


def vis_depth_edge_connectivity(depth, args):
    disp = 1. / depth
    u_diff = (disp[1:, :] - disp[:-1, :])[:-1, 1:-1]
    b_diff = (disp[:-1, :] - disp[1:, :])[1:, 1:-1]
    l_diff = (disp[:, 1:] - disp[:, :-1])[1:-1, :-1]
    r_diff = (disp[:, :-1] - disp[:, 1:])[1:-1, 1:]
    u_over = (np.abs(u_diff) > args.depth_threshold).astype(np.float32)
    b_over = (np.abs(b_diff) > args.depth_threshold).astype(np.float32)
    l_over = (np.abs(l_diff) > args.depth_threshold).astype(np.float32)
    r_over = (np.abs(r_diff) > args.depth_threshold).astype(np.float32)
    concat_diff = np.stack([u_diff, b_diff, r_diff, l_diff], axis=-1)
    concat_over = np.stack([u_over, b_over, r_over, l_over], axis=-1)
    over_diff = concat_diff * concat_over
    pos_over = (over_diff > 0).astype(np.float32).sum(-1).clip(0, 1)
    neg_over = (over_diff < 0).astype(np.float32).sum(-1).clip(0, 1)
    neg_over[(over_diff > 0).astype(np.float32).sum(-1) > 0] = 0
    _, edge_label = cv2.connectedComponents(
        pos_over.astype(np.uint8),
        connectivity=8
    )
    T_junction_maps = np.zeros_like(pos_over)
    for edge_id in range(1, edge_label.max() + 1):
        edge_map = (edge_label == edge_id).astype(np.uint8)
        edge_map = np.pad(edge_map, pad_width=((1, 1), (1, 1)), mode='constant')
        four_direc = np.roll(edge_map, 1, 1) + np.roll(
            edge_map,
            -1,
            1
        ) + np.roll(edge_map, 1, 0) + np.roll(edge_map, -1, 0)
        eight_direc = np.roll(np.roll(edge_map, 1, 1), 1, 0) + np.roll(
            np.roll(edge_map, 1, 1),
            -1,
            0
        ) + \
                      np.roll(np.roll(edge_map, -1, 1), 1, 0) + np.roll(
            np.roll(edge_map, -1, 1),
            -1,
            0
        )
        eight_direc = (eight_direc + four_direc)[1:-1, 1:-1]
        pos_over[eight_direc > 2] = 0
        T_junction_maps[eight_direc > 2] = 1
    _, edge_label = cv2.connectedComponents(
        pos_over.astype(np.uint8),
        connectivity=8
    )
    edge_label = np.pad(edge_label, 1, mode='constant')

    return edge_label


def max_size(mat, value=0):
    if not (mat and mat[0]):
        return (0, 0)
    it = iter(mat)
    prev = [(el == value) for el in next(it)]
    max_size = max_rectangle_size(prev)
    for row in it:
        hist = [(1 + h) if el == value else 0 for h, el in zip(prev, row)]
        max_size = max(max_size, max_rectangle_size(hist), key=get_area)
        prev = hist
    return max_size


def max_rectangle_size(histogram):
    Info = namedtuple('Info', 'start height')
    stack = []
    top = lambda: stack[-1]
    max_size = (0, 0)  # height, width of the largest rectangle
    pos = 0  # current position in the histogram
    for pos, height in enumerate(histogram):
        start = pos  # position where rectangle starts
        while True:
            if not stack or height > top().height:
                stack.append(Info(start, height))  # push
            if stack and height < top().height:
                max_size = max(
                    max_size, (top().height, (pos - top().start)),
                    key=get_area
                )
                start, _ = stack.pop()
                continue
            break  # height == top().height goes here

    pos += 1
    for start, height in stack:
        max_size = max(
            max_size, (height, (pos - start)),
            key=get_area
        )

    return max_size


def get_area(size):
    return reduce(mul, size)


def find_anchors(matrix):
    matrix = [[*x] for x in matrix]
    mh, mw = max_size(matrix)
    matrix = np.array(matrix)
    # element = np.zeros((mh, mw))
    for i in range(matrix.shape[0] + 1 - mh):
        for j in range(matrix.shape[1] + 1 - mw):
            if matrix[i:i + mh, j:j + mw].max() == 0:
                return i, i + mh, j, j + mw


def find_largest_rect(dst_img, bg_color=(128, 128, 128)):
    valid = np.any(dst_img[..., :3] != bg_color, axis=-1)
    dst_h, dst_w = dst_img.shape[:2]
    ret, labels = cv2.connectedComponents(np.uint8(valid == False))
    red_mat = np.zeros_like(labels)
    # denoise 
    for i in range(1, np.max(labels) + 1, 1):
        x, y, w, h = cv2.boundingRect(np.uint8(labels == i))
        if x == 0 or (x + w) == dst_h or y == 0 or (y + h) == dst_w:
            red_mat[labels == i] = 1
            # crop
    t, b, l, r = find_anchors(red_mat)

    return t, b, l, r
