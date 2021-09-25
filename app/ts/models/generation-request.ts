import {GenerationResult} from "./generation-result";
import {GenerationSpec} from "./generation-spec";
import {BaseModel} from "./base-model";

export class GenerationRequest extends BaseModel {
    spec: GenerationSpec;
    name ?: string;
    preview ?: string;
    interim ?: string;
    interim_watermarked ?: string;
    steps_completed ?: number;
    steps_total ?: number;
    results ?: GenerationResult[];

    started ?: string;
    completed ?: string;
    failed ?: string;
}
