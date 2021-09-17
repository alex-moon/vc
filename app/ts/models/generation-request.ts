import {GenerationResult} from "./generation-result";

export class GenerationRequest {
    name: string;
    preview ?: string;
    interim ?: string;
    steps_completed ?: number;
    steps_total ?: number;
    results ?: GenerationResult[];

    constructor(raw: any = null) {
        if (raw) {
            Object.assign(this, raw);
        }
    }
}
