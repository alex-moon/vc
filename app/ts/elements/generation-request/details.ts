import {CustomElement, Toggle, Watch} from 'custom-elements-ts';
import {GenerationRequest as Model} from "../../models/generation-request";
import {GenerationRequestDetailsStep} from "./step";
import {DetailsHelper, ImageCounter} from "../../helpers/details";
import {Chipset} from "../chipset";
import {AuthHelper} from "../../helpers/auth";
import {Vc} from "../../vc";
import {EnvHelper} from "../../helpers/env";

@CustomElement({
    tag: 'vc-generation-request-details',
    shadow: false,
    style: ``,
    template: `
<div class="details">
    <div class="preview"></div>
    <div class="steps"></div>
</div>
`
})
export class GenerationRequestDetails extends HTMLElement {
    $root: HTMLElement
    $actions: HTMLElement
    $steps: HTMLElement
    $preview: HTMLElement

    private vc: Vc
    private request: Model

    @Toggle() expanded = false

    constructor() {
        super();
    }

    inject() {
        // @todo injector of some kind?
        // https://nehalist.io/dependency-injection-in-typescript/
        // or https://www.npmjs.com/package/bottlejs
        this.vc = Vc.instance;
    }

    connectedCallback() {
        this.inject();
        this.$root = this.querySelector('.details');
        this.$steps = this.$root.querySelector('.steps');
        this.$preview = this.$root.querySelector('.preview');
    }

    update(request: Model) {
        this.request = request;
    }

    draw() {
        if (!this.expanded) {
            if (this.$actions) {
                this.$actions.remove();
            }
            this.$preview.innerHTML = '';
            this.$steps.innerHTML = '';
            return;
        }

        if (this.request.spec) {
            const images = this.request.spec.images;
            if (images && images.length) {
                for (let i = 0; i < images.length; i++) {
                    const element = document.createElement(
                        'vc-generation-request-details-step'
                    ) as GenerationRequestDetailsStep;
                    this.$steps.appendChild(element);
                    element.update(i + 1, images[i]);
                }
            }

            const videos = this.request.spec.videos;
            if (videos && videos.length) {
                for (const video of videos) {
                    const steps = video.steps;
                    for (let i = 0; i < steps.length; i++) {
                        const element = document.createElement(
                            'vc-generation-request-details-step'
                        ) as GenerationRequestDetailsStep;
                        this.$steps.appendChild(element);
                        element.update(i + 1, steps[i]);
                    }
                }
            }
        }

        let urls = DetailsHelper.getResultUrls(this.request);
        if (urls.length) {
            let counter = {next(): string[] { return []; }};
            if (this.request.spec) {
                counter = new ImageCounter(this.request.spec.images);
            }
            let panel;
            for (const url of urls) {
                if (url.substr(-4) === '.png') {
                    panel = this.createImagePanel(url, counter.next());
                } else {
                    panel = this.createVideoPanel(url);
                }
                this.$preview.appendChild(panel);
            }
        } else {
            const panel = this.createImagePanel('/assets/placeholder.png');
            this.$preview.appendChild(panel);
        }

        if (EnvHelper.useLocal) {
            return;
        }

        this.addActions();
    }

    createVideoPanel(url: string) {
        const video = document.createElement('video');
        video.setAttribute('controls', 'controls');
        video.setAttribute('width', '800');
        video.setAttribute('height', '800');

        const source = document.createElement('source');
        source.src = url;

        video.appendChild(source);
        return this.createPanel(video);
    }

    createImagePanel(url: string, chips: string[] = []) {
        const img = document.createElement('img');
        img.src = url;
        const panel = this.createPanel(img);
        const chipset = document.createElement('vc-chipset') as Chipset;
        panel.appendChild(chipset);
        chipset.update(chips.filter(text => text));
        return panel;
    }

    createPanel(element: HTMLElement) {
        const panel = document.createElement('div');
        panel.setAttribute('class', 'panel');
        panel.appendChild(element);
        return panel;
    }

    addActions() {
        if (AuthHelper.hasToken()) {
            this.$actions = document.createElement('div');
            this.$actions.classList.add('actions');
            this.$root.insertBefore(this.$actions, this.$root.firstChild);
            if (this.request.published) {
                this.addAction('Unpublish', 'remove_circle', (e: MouseEvent) => {
                    if (window.confirm('Are you sure you would like to unpublish this request?')) {
                        this.vc.unpublish(this.request);
                    }
                });
            } else {
                this.addAction('Publish', 'publish', (e: MouseEvent) => {
                    if (window.confirm('Are you sure you would like to publish this request?')) {
                        this.vc.publish(this.request);
                    }
                });
            }
            if (!this.request.cancelled && !this.request.failed && !this.request.completed) {
                this.addAction('Cancel job', 'cancel', (e: MouseEvent) => {
                    if (window.confirm('Are you sure you would like to cancel this request?')) {
                        this.vc.cancel(this.request);
                    }
                }, 'warn');
            } else {
                this.addAction('Retry job', 'restart_alt', (e: MouseEvent) => {
                    if (window.confirm('Are you sure you would like to restart this request?')) {
                        this.vc.retry(this.request);
                    }
                });
                this.addAction('Delete job', 'delete', (e: MouseEvent) => {
                    if (window.confirm('Are you sure you would like to delete this request?')) {
                        this.vc.delete(this.request);
                    }
                }, 'warn');
            }
        }
    }

    addAction(
        label: string,
        iconString: string,
        callback: (e: MouseEvent) => void,
        cssClass: string = null
    ) {
        const button = document.createElement('button')
        button.innerText = label;
        if (cssClass) {
            button.classList.add(cssClass);
        }
        const icon = document.createElement('span');
        icon.classList.add('material-icons');
        icon.innerText = iconString;
        button.insertBefore(icon, button.firstChild);
        this.$actions.appendChild(button);
        button.addEventListener('click', callback);
    }

    @Watch('expanded')
    protected onExpandedChange() {
        if (this.expanded) {
            this.$root.classList.add('expanded');
        } else {
            this.$root.classList.remove('expanded');
        }
        this.draw();
    }
}
