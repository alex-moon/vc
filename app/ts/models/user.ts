import {BaseModel} from "./base-model";

export class User extends BaseModel {
    name ?: string;
    email ?: string;
    tier ?: number;
}
