import {CustomElement, Prop} from 'custom-elements-ts';

interface Article {
    url: string;
    title: string;
    hero ?: string;
    author ?: string;
    published ?: string;
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

    articles: Article[] = [
        {
            url: 'foss',
            title: 'vc is open source now!',
            hero: 'foss',
            author: 'AJ Moon',
            published: '16 November, 2021',
        },
        {
            url: '',
            title: 'Welcome to vc',
            hero: 'index',
        },
    ];

    constructor() {
        super();
    }

    connectedCallback() {
        this.$root = this.querySelector('.nav-container');
        this.$nav = this.$root.querySelector('.nav');
        this.articles.forEach(this.addLink.bind(this));
    }

    addLink(article: Article) {
        const a = document.createElement('a');
        a.href = '/news/' + article.url;
        if (this.active === article.url) {
            a.classList.add('active');
        }

        const hero = document.createElement('div');
        hero.classList.add('hero');
        const img = document.createElement('img');
        img.src = '/assets/news/' + (article.hero || '../placeholder') + '.png';
        hero.appendChild(img);
        a.appendChild(hero);

        const content = document.createElement('div');
        content.classList.add('content');

        const title = document.createElement('h3');
        title.innerText = article.title;
        content.appendChild(title);

        const byline = document.createElement('div');
        byline.classList.add('byline');

        if (article.author) {
            const author = document.createElement('div');
            author.classList.add('author');
            author.innerText = article.author;
            byline.appendChild(author);
        }
        if (article.published) {
            const published = document.createElement('div');
            published.classList.add('published');
            published.innerText = article.published;
            byline.appendChild(published);
        }

        content.appendChild(byline);
        a.appendChild(content);
        console.log('appending link', a);
        this.$nav.appendChild(a);
    }
}
