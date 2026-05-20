import { LoginScreen } from "@/components/login-screen";
import { redirectIfAuthenticated } from "@/lib/server-auth";

export default async function LoginPage() {
  await redirectIfAuthenticated();
  return <LoginScreen />;
}
