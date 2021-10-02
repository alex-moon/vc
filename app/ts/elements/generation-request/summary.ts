import {CustomElement, Dispatch, DispatchEmitter} from 'custom-elements-ts';
import {GenerationRequest as Model} from "../../models/generation-request";
import {StatusHelper} from "../../helpers/status";
import {DetailsHelper} from "../../helpers/details";
import {AuthHelper} from "../../helpers/auth";
import {Service} from "../../service";

@CustomElement({
    tag: 'vc-generation-request-summary',
    shadow: false,
    style: ``,
    template: `
<div class="summary">
    <div class="preview">
        <img src="/assets/placeholder.png"/>
    </div>
    <div class="progress">
        <div class="labels">
            <div class="name"></div>
            <div class="status"></div>
        </div>
        <div class="bar">
            <div class="completed"></div>
            <div class="steps">
                <span class="steps-completed"></span>
                /
                <span class="steps-total"></span>
            </div>
        </div>
    </div>
</div>
`
})
export class GenerationRequestSummary extends HTMLElement {
    $root: HTMLElement
    $name: HTMLElement
    $status: HTMLElement

    $stepsCompleted: HTMLElement
    $stepsTotal: HTMLElement
    $barCompleted: HTMLElement
    $preview: HTMLImageElement
    $expand: HTMLElement

    service: Service
    request: Model
    expanded = false

    @Dispatch('summary.expand') expand: DispatchEmitter

    constructor() {
        super();
    }

    inject() {
        // @todo injector of some kind?
        // https://nehalist.io/dependency-injection-in-typescript/
        // or https://www.npmjs.com/package/bottlejs
        this.service = (window as any).vc.service;
    }

    connectedCallback() {
        this.inject();
        this.$root = this.querySelector('.summary');
        this.$name = this.$root.querySelector('.name');
        this.$status = this.$root.querySelector('.status');

        this.$stepsCompleted = this.$root.querySelector('.steps-completed');
        this.$stepsTotal = this.$root.querySelector('.steps-total');
        this.$barCompleted = this.$root.querySelector('.bar .completed');
        this.$preview = this.$root.querySelector('.preview img');
    }

    update(request: Model) {
        this.request = request;
        this.$name.textContent = this.request.name;
        this.$stepsCompleted.textContent = '' + (this.request.steps_completed || '?');
        this.$stepsTotal.textContent = '' + (this.request.steps_total || '?');

        this.updateStatus(
            this.request.created,
            this.request.started,
            this.request.completed,
            this.request.failed
        );
        this.updateBar(
            this.request.steps_completed,
            this.request.steps_total
        );
        if (DetailsHelper.hasDetails(this.request)) {
            this.addExpand();
        }

        this.$preview.src = this.request.preview || '/assets/placeholder.png';
    }

    updateStatus(
        created: string,
        started: string,
        completed: string,
        failed: string
    ) {
        this.$status.classList.remove('queued', 'started', 'completed', 'failed');
        this.$status.innerHTML = '';

        let {slug, readable, datetime} = StatusHelper.get(this.request);

        this.$status.classList.add(slug);

        let child = document.createElement('div');
        child.classList.add('readable');
        child.innerHTML = readable;
        this.$status.appendChild(child);

        child = document.createElement('div');
        child.classList.add('datetime');
        child.innerHTML = datetime;
        this.$status.appendChild(child);
    }

    addExpand() {
        const actions = document.createElement('div');
        actions.classList.add('actions');

        if (AuthHelper.hasToken()) {
            if (!this.request.cancelled && !this.request.failed && !this.request.completed) {
                const cancel = document.createElement('button')
                cancel.classList.add('material-icons');
                cancel.innerText = 'cancel';
                actions.appendChild(cancel);
                cancel.addEventListener('click', (e: MouseEvent) => {
                    this.service.cancel(this.request, this.update.bind(this));
                });
            } else {
                const button = document.createElement('button')
                button.classList.add('material-icons');
                button.innerText = 'delete';
                actions.appendChild(button);
                button.addEventListener('click', (e: MouseEvent) => {
                    this.service.delete(this.request, this.update.bind(this));
                });
            }
        }

        const expand = document.createElement('button');
        expand.classList.add('material-icons');
        expand.innerText = 'expand_more';
        actions.appendChild(expand);

        expand.addEventListener('click', (e: MouseEvent) => {
            if (this.expanded) {
                expand.innerText = 'expand_more';
                this.expanded = false;
                this.$root.classList.remove('expanded');
            } else {
                expand.innerText = 'expand_less';
                this.expanded = true;
                this.$root.classList.add('expanded');
            }
            this.expand.emit({detail: this.expanded});
        });

        this.$root.appendChild(actions);
    }

    updateBar(completed: number, total: number) {
        let percentage = 0;
        if (total > 0) {
            percentage = 100 * completed / total
        }
        this.$barCompleted.setAttribute(
            'style',
            'width: ' + percentage + '%'
        )
    }
}
