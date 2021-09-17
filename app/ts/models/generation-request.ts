import {GenerationResult} from "./generation-result";
import {GenerationSpec} from "./generation-spec";

export class GenerationRequest {
    spec: GenerationSpec;
    name: string;
    preview ?: string;
    interim ?: string;
    steps_completed ?: number;
    steps_total ?: number;
    results ?: GenerationResult[];
}
