const dayjs = require('dayjs');

export enum StatusSlug {
    QUEUED = 'queued',
    STARTED = 'started',
    COMPLETED = 'completed',
    FAILED = 'failed',
}

export interface Status {
    slug: string;
    readable: string;
    datetime: string;
}

export class StatusHelper {
    static DATETIME_FORMAT = 'ddd D MMM [at] h:mma';

    static get(created: string, started: string, completed: string, failed: string) {
        let slug = StatusSlug.QUEUED;
        let readable = 'Queued';
        let datetime = dayjs(created);
        if (started) {
            slug = StatusSlug.STARTED;
            readable = 'Started';
            datetime = dayjs(started);
            if (completed) {
                slug = StatusSlug.COMPLETED;
                readable = 'Completed';
                datetime = dayjs(completed);
            } else if (failed) {
                slug = StatusSlug.FAILED;
                readable = 'Failed';
                datetime = dayjs(failed);
            }
        }
        datetime = datetime.format(StatusHelper.DATETIME_FORMAT);
        return {slug, readable, datetime} as Status;
    }
}
