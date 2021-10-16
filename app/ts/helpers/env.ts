export class EnvHelper {
    static get useLocal(): boolean {
        return (window as any).env.useLocal;
    }
    static get host(): string {
        return (window as any).env.host;
    }
}
