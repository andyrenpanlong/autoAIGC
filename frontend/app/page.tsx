import { redirect } from "next/navigation";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import Dashboard from "@/components/dashboard/dashboard";

export default async function HomePage() {
  const session = await getServerSession(authOptions);
  
  // 如果用户未登录，重定向到登录页面
  if (!session) {
    redirect("/auth/login");
  }
  
  return <Dashboard />;
}
