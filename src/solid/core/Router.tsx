import { Router, Route } from "@solidjs/router";
import AppShell from "./AppShell";
import ChatWindow from "../brain/ChatWindow";
import VaultPage from "../vault/VaultPage";
import StudioPage from "../studio/StudioPage";
import LocalSettings from "../components/settings/LocalSettings";
import GuidePage from "../guide/GuidePage";

export default function AppRouter() {
    return (
        <Router root={AppShell}>
            <Route path="/" component={ChatWindow} />
            <Route path="/brain" component={ChatWindow} />
            <Route path="/vault" component={VaultPage} />
            <Route path="/studio" component={StudioPage} />
            <Route path="/settings" component={LocalSettings} />
            <Route path="/guide" component={GuidePage} />
        </Router>
    );
}
