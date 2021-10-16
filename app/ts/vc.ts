import {Service} from './service'
import {GenerationRequests} from './elements/generation-requests'
import {GenerationRequestForm} from "./elements/generation-request-form";
import {ImageSpec} from "./models/image-spec";
import {AuthHelper} from "./helpers/auth";
import {GenerationRequest} from "./models/generation-request";
import {Info} from "./elements/info";
import {EnvHelper} from "./helpers/env";

export class Vc {
    $info: Info;
    $form: GenerationRequestForm;
    $requests: GenerationRequests;

    refreshInterval = 10000
    autoRefresh = false
    timeout: any
    service: Service

    constructor() {
        this.service = new Service();
        this.$requests = document.querySelector('vc-generation-requests');
        this.refreshAndSetTimeout();
        AuthHelper.listen(this.refresh.bind(this));
        this.bindEvents();
        if (EnvHelper.useLocal) {
            setTimeout(this.toggleInfo.bind(this));
        }
    }

    static get instance() {
        return (global as any).vc;
    }

    bindEvents() {
        const info = document.querySelector('.info.header-button');
        info.addEventListener('click', this.toggleInfo.bind(this));
    }
    
    toggleInfo() {
        this.$info = document.querySelector('vc-info');
        this.$info.expand();
    }

    create(spec: ImageSpec) {
        this.service.create(spec, this.draw.bind(this));
    }

    clearTimeout() {
        window.clearTimeout(this.timeout);
    }

    setTimeout() {
        this.timeout = window.setTimeout(
            this.refreshAndSetTimeout.bind(this),
            this.refreshInterval
        );
    }

    refreshAndSetTimeout() {
        this.refresh();
        if (this.autoRefresh) {
            this.setTimeout();
        }
    }

    setAutoRefresh(value: boolean) {
        this.autoRefresh = value;
        if (this.autoRefresh) {
            this.setTimeout();
        } else {
            this.clearTimeout();
        }
    }

    refresh() {
        this.service.refresh(this.draw.bind(this));
    }

    cancel(request: GenerationRequest) {
        this.service.cancel(request, this.refresh.bind(this));
    }

    retry(request: GenerationRequest) {
        this.service.retry(request, this.refresh.bind(this));
    }

    delete(request: GenerationRequest) {
        this.service.delete(request, this.refresh.bind(this));
    }

    publish(request: GenerationRequest) {
        this.service.publish(request, this.refresh.bind(this));
    }

    unpublish(request: GenerationRequest) {
        this.service.unpublish(request, this.refresh.bind(this));
    }

    draw(requests: any) {
        this.$requests.update(requests);
    }
}

(global as any).vc = new Vc();
