import {CustomElement} from 'custom-elements-ts';

@CustomElement({
    tag: 'vc-info',
    shadow: false,
    style: ``,
    template: `
<div class="info">
    <h2><strong>vc</strong>: Virtual Content</h2>
    <h3>What's it all about then?</h3>
    <p>
        <strong>vc</strong> is a digital art project by North East England-based British/Australian
        software engineer <a target="_blank" href="https://twitter.com/alexmoonpro">Alex Moon</a>.
    </p>
    <p>
        Combining existing AI/machine learning technologies to create explorable dream
        worlds, <strong>vc</strong> is a series of short videos which employs a poetic approach
        to the emerging form that is AI-generated visual art.
    </p>
    <p>
        Human and machine collaborate to give expression
        to the latent content of an unprecedented technological age. 
    </p>
    <h3>Buy the artwork</h3>
    <p>
        Individual videos are available to purchase as NFTs on
        <a target="_blank" href="https://opensea.io/collection/vc-ajmoon-uk">OpenSea</a>.
    </p>
    <p>
        Each piece is delicately crafted with care and attention. Much time, effort
        and engineering expertise have gone into making these works a reality.
    </p>
    <p>
        Many AI artists are already using VQGAN/CLIP. These works go a step further, using
        3D Photo Inpainting and Image Super Resolution to move a camera iteratively inside
        the generated space. No-one else is doing this... yet. Be among the first to own a
        piece of history.
    </p>
    <h3>Acknowledgements</h3>
    <p>
        This work is built on the shoulders of giants, including:
        <ul>
            <li><a target="_blank" href="https://twitter.com/advadnoun">Ryan Murdock</a></li>
            <li><a target="_blank" href="https://twitter.com/rivershavewings">Katherine Crowson</a></li>
            <li><a target="_blank" href="https://shihmengli.github.io/3D-Photo-Inpainting">Shih, Meng-Li and Su, Shih-Yang and Kopf, Johannes and Huang, Jia-Bin</a></li>
            <li><a target="_blank" href="https://idealo.github.io/image-super-resolution">Francesco Cardinale et al.</a></li>
        </ul>    
    </p>
    <p><!-- extra space for mobile browsers @todo more elegant solution --></p>
</div>
`
})
export class Info extends HTMLElement {
    $root: HTMLElement
    expanded = false;

    constructor() {
        super();
    }

    connectedCallback() {
        this.$root = this.querySelector('.info');
    }

    expand() {
        this.expanded = !this.expanded;
        if (this.expanded) {
            this.$root.classList.add('expanded');
        } else {
            this.$root.classList.remove('expanded');
        }
    }
}
