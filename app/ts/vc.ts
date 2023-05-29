import {GenerationRequestManager} from './managers/generation-request-manager'
import {GenerationRequests} from './elements/generation-requests'
import {AuthHelper} from "./helpers/auth";
import {GenerationRequest} from "./models/generation-request";
import {GenerationSpec} from "./models/generation-spec";
import {UserManager} from "./managers/user-manager";
import {Notification} from "./helpers/notification";

export class Vc {
    $requests: GenerationRequests;

    refreshInterval = 10000
    autoRefresh = false
    timeout: any

    constructor(
        public generationRequestManager: GenerationRequestManager,
        public userManager: UserManager,
        public notification: Notification,
    ) {
        this.$requests = document.querySelector('vc-generation-requests');
        if (this.$requests) {
            this.authenticate();
            AuthHelper.listen(this.refresh.bind(this));
        }
    }

    static get instance() {
        return (global as any).vc;
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

    private error(error: Error) {
        this.notification.error(error);
    }

    authenticate(token: string = null) {
        AuthHelper.setToken(token);
        this.userManager.get().then(() => {
            AuthHelper.authenticate();
        }).catch((error) => {
            AuthHelper.clearToken();
            if (token !== null) {
                this.error(error);
            } else {
                this.refreshAndSetTimeout();
            }
        });
    }

    refresh() {
        this.generationRequestManager.index()
            .then(this.draw.bind(this))
            .catch(this.error.bind(this));
    }

    create(spec: GenerationSpec) {
        this.generationRequestManager.create({spec})
            .then(this.refresh.bind(this))
            .catch(this.error.bind(this));
    }

    cancel(request: GenerationRequest) {
        this.generationRequestManager.cancel(request.id)
            .then(this.refresh.bind(this))
            .catch(this.error.bind(this));
    }

    retry(request: GenerationRequest) {
        this.generationRequestManager.retry(request.id)
            .then(this.refresh.bind(this))
            .catch(this.error.bind(this));
    }

    delete(request: GenerationRequest) {
        this.generationRequestManager.delete(request.id)
            .then(this.refresh.bind(this))
            .catch(this.error.bind(this));
    }

    publish(request: GenerationRequest) {
        this.generationRequestManager.publish(request.id)
            .then(this.refresh.bind(this))
            .catch(this.error.bind(this));
    }

    unpublish(request: GenerationRequest) {
        this.generationRequestManager.unpublish(request.id)
            .then(this.refresh.bind(this))
            .catch(this.error.bind(this));
    }

    draw(requests: GenerationRequest[]) {
        this.$requests.update(requests);
    }
}

// @todo do we need a container? Surely not...
(global as any).vc = new Vc(
    new GenerationRequestManager(),
    new UserManager(),
    new Notification(),
);
