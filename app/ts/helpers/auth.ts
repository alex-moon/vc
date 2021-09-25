export class AuthHelper {
    token: string = null;

    public setToken(token: string) {
        this.token = token;
    }

    public hasToken() {
        return this.token !== null;
    }
}
