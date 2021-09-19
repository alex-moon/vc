import {CustomElement, Dispatch, DispatchEmitter} from 'custom-elements-ts';
import {GenerationRequest as Model} from "../../models/generation-request";
import {StatusHelper} from "../../helpers/status";

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
    <div class="actions">
        <button class="material-icons">
            expand_more
        </button>
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

    request: Model
    expanded = false

    @Dispatch('summary.expand') expand: DispatchEmitter

    constructor() {
        super();
    }

    connectedCallback() {
        this.$root = this.querySelector('.summary');
        this.$name = this.$root.querySelector('.name');
        this.$status = this.$root.querySelector('.status');

        this.$stepsCompleted = this.$root.querySelector('.steps-completed');
        this.$stepsTotal = this.$root.querySelector('.steps-total');
        this.$barCompleted = this.$root.querySelector('.bar .completed');
        this.$preview = this.$root.querySelector('.preview img');
        this.$expand = this.$root.querySelector('.actions button');

        this.$expand.addEventListener('click', (e) => {
            if (this.expanded) {
                this.$expand.innerHTML = 'expand_more';
                this.expanded = false;
                this.$root.classList.remove('expanded');
            } else {
                this.$expand.innerHTML = 'expand_less';
                this.expanded = true;
                this.$root.classList.add('expanded');
            }
            this.expand.emit({detail: this.expanded});
        });
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

        let {slug, readable, datetime} = StatusHelper.get(created, started, completed, failed);

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
