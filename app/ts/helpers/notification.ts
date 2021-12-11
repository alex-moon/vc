import {Unnotify} from "../lib/unnotify";

export class Notification {
    private un: Unnotify = null;

    public constructor() {
        this.un = new Unnotify('right', true);
    }

    public error(error: Error, message: string = null, title: string = null) {
        let content = error.message;
        if (message !== null) {
            content += ': ' + message;
        }
        if (title === null) {
            title = 'Something went wrong';
        }
        this.show(title, content, 'danger');
    }

    private show(title: string, content: string, type: string) {
        this.un.show(title, content, {type});
    }
}
