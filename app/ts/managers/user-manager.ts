import {User} from "../models/user";
import {BaseManager} from "./base-manager";

// @todo BaseManager
export class UserManager extends BaseManager<User> {
    base_url = '/api/user/me'

    get(): Promise<User> {
        return this.fetch() as Promise<User>;
    }
}
