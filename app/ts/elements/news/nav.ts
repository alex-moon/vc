import {CustomElement, Prop} from 'custom-elements-ts';

interface Article {
    url: string;
    title: string;
    author: string;
    published: string;
}

@CustomElement({
    tag: 'vc-nav',
    shadow: false,
    style: ``,
    template: `
<div class="nav-container">
    <div class="nav"></div>
</div>
`
})
export class Nav extends HTMLElement {
    $root: HTMLElement;
    $nav: HTMLElement;

    @Prop() active: string;

    expanded = false;
    articles: Article[] = [
        {
            url: 'foss',
            title: 'vc is open source now!',
            author: 'AJ Moon',
            published: '16 November, 2021',
        }
    ];

    constructor() {
        super();
    }

    connectedCallback() {
        this.$root = this.querySelector('.nav-container');
        this.$nav = this.$root.querySelector('.nav');
        this.articles.forEach(this.addLink.bind(this));
    }

    expand() {
        this.expanded = !this.expanded;
        if (this.expanded) {
            this.$root.classList.add('expanded');
        } else {
            this.$root.classList.remove('expanded');
        }
    }

    addLink(article: Article) {
        const a = document.createElement('a');
        a.href = '/news/' + article.url;
        if (this.active === article.url) {
            a.classList.add('active');
        }
        const avatar = document.createElement('div');
        avatar.classList.add('avatar');
        a.appendChild(avatar);
        const content = document.createElement('div');
        content.classList.add('content');
        const title = document.createElement('h3');
        title.innerText = article.title;
        content.appendChild(title);
        const byline = document.createElement('div');
        byline.classList.add('byline');
        const author = document.createElement('div');
        author.classList.add('author');
        author.innerText = article.author;
        const published = document.createElement('div');
        published.classList.add('published');
        published.innerText = article.published;
        byline.appendChild(author);
        byline.appendChild(published);
        content.appendChild(byline);
        a.appendChild(content);
        console.log('appending link', a);
        this.$nav.appendChild(a);
    }
}
