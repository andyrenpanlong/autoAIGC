import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/theme-provider";
import { Toaster } from "react-hot-toast";
import { AuthProvider } from "@/components/auth-provider";
import { QueryProvider } from "@/components/query-provider";
import { Navbar } from "@/components/navbar";
import { Sidebar } from "@/components/sidebar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AI Video Generator - Create Stunning Videos with AI",
  description: "Generate professional videos from text, images, and scripts using advanced AI models. Perfect for short dramas, advertisements, and social media content.",
  keywords: ["AI video", "video generation", "text to video", "AI short film", "video creator", "LTX", "Stable Diffusion", "Sora"],
  authors: [{ name: "AI Video Platform" }],
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://ai-video-platform.com",
    title: "AI Video Generator",
    description: "Create stunning videos with AI in minutes",
    siteName: "AI Video Platform",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "AI Video Generator",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "AI Video Generator",
    description: "Create stunning videos with AI in minutes",
    images: ["/twitter-image.png"],
    creator: "@aivideoplatform",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.className} antialiased`}>
        <QueryProvider>
          <ThemeProvider
            attribute="class"
            defaultTheme="system"
            enableSystem
            disableTransitionOnChange
          >
            <AuthProvider>
              <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/30">
                <div className="fixed inset-0 grid-background -z-10" />
                
                <div className="flex min-h-screen">
                  {/* 侧边栏 */}
                  <Sidebar />
                  
                  <div className="flex-1 flex flex-col">
                    {/* 导航栏 */}
                    <Navbar />
                    
                    {/* 主内容区域 */}
                    <main className="flex-1 p-6 overflow-auto">
                      <div className="max-w-7xl mx-auto">
                        {children}
                      </div>
                    </main>
                    
                    {/* 页脚 */}
                    <footer className="border-t py-6 px-6">
                      <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
                        <div className="text-sm text-muted-foreground">
                          <p>© 2024 AI Video Platform. All rights reserved.</p>
                          <p className="mt-1">Powered by LTX 2.3, Stable Diffusion, and advanced AI models.</p>
                        </div>
                        <div className="flex items-center gap-6">
                          <a href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                            Privacy Policy
                          </a>
                          <a href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                            Terms of Service
                          </a>
                          <a href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                            Contact
                          </a>
                        </div>
                      </div>
                    </footer>
                  </div>
                </div>
                
                {/* Toast通知 */}
                <Toaster
                  position="top-right"
                  toastOptions={{
                    duration: 4000,
                    style: {
                      background: "hsl(var(--background))",
                      color: "hsl(var(--foreground))",
                      border: "1px solid hsl(var(--border))",
                    },
                    success: {
                      iconTheme: {
                        primary: "hsl(var(--primary))",
                        secondary: "hsl(var(--primary-foreground))",
                      },
                    },
                    error: {
                      iconTheme: {
                        primary: "hsl(var(--destructive))",
                        secondary: "hsl(var(--destructive-foreground))",
                      },
                    },
                  }}
                />
              </div>
            </AuthProvider>
          </ThemeProvider>
        </QueryProvider>
      </body>
    </html>
  );
}
