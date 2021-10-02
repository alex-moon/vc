import {GenerationRequest} from "../models/generation-request";

const dayjs = require('dayjs');

export enum StatusSlug {
    QUEUED = 'queued',
    STARTED = 'started',
    COMPLETED = 'completed',
    FAILED = 'failed',
    CANCELLED = 'cancelled',
}

export interface Status {
    slug: string;
    readable: string;
    datetime: string;
}

export class StatusHelper {
    static DATETIME_FORMAT = 'ddd D MMM [at] h:mma';

    static get(request: GenerationRequest) {
        let slug = StatusSlug.QUEUED;
        let readable = 'Queued';
        let datetime = dayjs(request.created);
        if (request.started) {
            slug = StatusSlug.STARTED;
            readable = 'Started';
            datetime = dayjs(request.started);
            if (request.completed) {
                slug = StatusSlug.COMPLETED;
                readable = 'Completed';
                datetime = dayjs(request.completed);
            } else if (request.failed) {
                slug = StatusSlug.FAILED;
                readable = 'Failed';
                datetime = dayjs(request.failed);
            } else if (request.cancelled) {
                slug = StatusSlug.CANCELLED;
                readable = 'Cancelled';
                datetime = dayjs(request.cancelled);
            }
        }
        datetime = datetime.format(StatusHelper.DATETIME_FORMAT);
        return {slug, readable, datetime} as Status;
    }
}
