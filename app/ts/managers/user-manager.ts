import {User} from "../models/user";
import {BaseManager} from "./base-manager";

// @todo BaseManager
export class UserManager extends BaseManager<User> {
    base_url = '/api/user/me'

    public user: User;

    get(): Promise<User> {
        return this.fetch().then((user) => {
            user = user as User;
            this.user = user;
            return user;
        });
    }
}
