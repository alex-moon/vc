import {GenerationRequest} from "../models/generation-request";

const dayjs = require('dayjs');

export enum StatusField {
    QUEUED = 'created',
    STARTED = 'started',
    COMPLETED = 'completed',
    FAILED = 'failed',
    CANCELLED = 'cancelled',
    RETRIED = 'retried',
}

export class Status {
    static DATETIME_FORMAT = 'ddd D MMM [at] h:mma';

    field: StatusField;
    value: string;
    constructor(field: StatusField, value: string) {
        this.field = field;
        this.value = value;
    }
    get readable() {
        return {
            [StatusField.QUEUED]: 'Queued',
            [StatusField.STARTED]: 'Started',
            [StatusField.COMPLETED]: 'Completed',
            [StatusField.FAILED]: 'Failed',
            [StatusField.CANCELLED]: 'Cancelled',
            [StatusField.RETRIED]: 'Restarted',
        }[this.field];
    }
    get datetime() {
        return dayjs(this.value).format(Status.DATETIME_FORMAT);
    }
}

export class StatusHelper {
    static get(request: GenerationRequest) {
        const [field, value] = StatusHelper.getMostRecent(request);
        return new Status(field, value);
    }

    private static getMostRecent(request: GenerationRequest) {
        let latestValue = null;
        let latestField = null;
        for (const field of Object.values(StatusField)) {
            const value = (request as any)[field];
            if (latestField === null) {
                latestField = field;
            }
            if (latestValue === null) {
                latestValue = value;
            }
            if (value > latestValue) {
                latestValue = value;
                latestField = field;
            }
        }
        return [latestField, latestValue];
    }
}
