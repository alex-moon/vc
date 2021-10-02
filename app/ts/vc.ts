import {Service} from './service'
import {GenerationRequests} from './elements/generation-requests'
import {GenerationRequestForm} from "./elements/generation-request-form";
import {ImageSpec} from "./models/image-spec";
import {AuthHelper} from "./helpers/auth";
import {GenerationRequest} from "./models/generation-request";

export class Vc {
    $form: GenerationRequestForm;
    $requests: GenerationRequests;

    refreshInterval = 10000
    autoRefresh = false
    timeout: any
    service: Service

    constructor() {
        this.service = new Service();
        this.$form = document.querySelector('vc-login-form');
        this.$form.connect(this);
        this.$requests = document.querySelector('vc-generation-requests');
        this.refreshAndSetTimeout();
        AuthHelper.listen(this.refresh.bind(this));
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

    delete(request: GenerationRequest) {
        this.service.delete(request, this.refresh.bind(this));
    }

    draw(requests: any) {
        this.$requests.update(requests);
    }
}

(global as any).vc = new Vc();
