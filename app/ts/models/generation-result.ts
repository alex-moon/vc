export class GenerationResult {
    url: string;

    constructor(raw: any = null) {
        if (raw) {
            Object.assign(this, raw);
        }
    }
}
