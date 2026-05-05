"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Video, 
  FileText, 
  Image, 
  PlayCircle, 
  Users, 
  Clock, 
  TrendingUp,
  Zap,
  Sparkles,
  Rocket,
  Brain,
  Palette,
  Film
} from "lucide-react";
import { useRouter } from "next/navigation";
import { useToast } from "@/hooks/use-toast";

// 模拟数据
const mockStats = {
  totalProjects: 12,
  totalVideos: 48,
  totalScripts: 36,
  totalStoryboards: 24,
  activeGenerations: 3,
  creditsUsed: 120,
  creditsRemaining: 380,
};

const recentProjects = [
  { id: 1, name: "夏日广告系列", type: "advertisement", progress: 85, status: "in_progress", lastUpdated: "2小时前" },
  { id: 2, name: "产品演示视频", type: "product_demo", progress: 100, status: "completed", lastUpdated: "1天前" },
  { id: 3, name: "社交媒体短剧", type: "short_drama", progress: 45, status: "in_progress", lastUpdated: "3小时前" },
  { id: 4, name: "教育教程", type: "educational", progress: 10, status: "draft", lastUpdated: "1周前" },
];

const quickActions = [
  { 
    id: 1, 
    title: "文生视频", 
    description: "从文本生成视频", 
    icon: FileText, 
    color: "bg-gradient-to-br from-blue-500 to-purple-600",
    href: "/generate/text-to-video"
  },
  { 
    id: 2, 
    title: "图生视频", 
    description: "从图像生成视频", 
    icon: Image, 
    color: "bg-gradient-to-br from-green-500 to-teal-600",
    href: "/generate/image-to-video"
  },
  { 
    id: 3, 
    title: "剧本生成", 
    description: "AI生成完整剧本", 
    icon: Brain, 
    color: "bg-gradient-to-br from-orange-500 to-red-600",
    href: "/scripts/generate"
  },
  { 
    id: 4, 
    title: "分镜设计", 
    description: "可视化分镜规划", 
    icon: Palette, 
    color: "bg-gradient-to-br from-purple-500 to-pink-600",
    href: "/storyboards/create"
  },
];

const aiModels = [
  { name: "LTX 2.3", type: "local", status: "available", speed: "fast", quality: "high" },
  { name: "Stable Video", type: "local", status: "available", speed: "medium", quality: "high" },
  { name: "OpenAI Sora", type: "cloud", status: "available", speed: "fast", quality: "excellent" },
  { name: "Runway Gen-2", type: "cloud", status: "available", speed: "medium", quality: "high" },
  { name: "Pika Labs", type: "cloud", status: "available", speed: "very fast", quality: "good" },
];

export default function Dashboard() {
  const router = useRouter();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(true);
  const [stats, setStats] = useState(mockStats);

  useEffect(() => {
    // 模拟加载数据
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  const handleQuickAction = (href: string) => {
    router.push(href);
  };

  const handleCreateProject = () => {
    toast({
      title: "创建新项目",
      description: "正在打开项目创建表单...",
    });
    router.push("/projects/create");
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed": return "bg-green-500";
      case "in_progress": return "bg-blue-500";
      case "draft": return "bg-gray-500";
      default: return "bg-gray-500";
    }
  };

  const getTypeLabel = (type: string) => {
    switch (type) {
      case "advertisement": return "广告";
      case "product_demo": return "产品演示";
      case "short_drama": return "短剧";
      case "educational": return "教育";
      default: return type;
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-muted-foreground">加载仪表板数据...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 欢迎横幅 */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-ai p-8 text-white">
        <div className="relative z-10">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-2">欢迎回来！</h1>
              <p className="text-white/80 mb-6 max-w-2xl">
                使用最先进的AI技术，快速创建令人惊叹的视频内容。从剧本到成片，一站式解决方案。
              </p>
              <div className="flex gap-4">
                <Button 
                  size="lg" 
                  className="bg-white text-primary hover:bg-white/90"
                  onClick={handleCreateProject}
                >
                  <Rocket className="mr-2 h-5 w-5" />
                  创建新项目
                </Button>
                <Button 
                  size="lg" 
                  variant="outline" 
                  className="bg-transparent border-white text-white hover:bg-white/10"
                  onClick={() => router.push("/templates")}
                >
                  <Sparkles className="mr-2 h-5 w-5" />
                  使用模板
                </Button>
              </div>
            </div>
            <div className="hidden lg:block">
              <Film className="h-32 w-32 opacity-20" />
            </div>
          </div>
        </div>
        <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-white/10 to-transparent rounded-full -translate-y-32 translate-x-32"></div>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">总项目数</CardTitle>
            <Video className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalProjects}</div>
            <p className="text-xs text-muted-foreground">+2 本周新增</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">生成视频</CardTitle>
            <PlayCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalVideos}</div>
            <p className="text-xs text-muted-foreground">+12 本月新增</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">剩余积分</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.creditsRemaining}</div>
            <Progress value={(stats.creditsUsed / (stats.creditsUsed + stats.creditsRemaining)) * 100} className="mt-2" />
            <p className="text-xs text-muted-foreground mt-1">已使用 {stats.creditsUsed} 积分</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">活跃生成</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.activeGenerations}</div>
            <p className="text-xs text-muted-foreground">3个正在处理中</p>
          </CardContent>
        </Card>
      </div>

      {/* 主要内容区域 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 左侧：快速操作和最近项目 */}
        <div className="lg:col-span-2 space-y-6">
          {/* 快速操作 */}
          <Card>
            <CardHeader>
              <CardTitle>快速开始</CardTitle>
              <CardDescription>选择一种方式开始创建内容</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {quickActions.map((action) => {
                  const Icon = action.icon;
                  return (
                    <button
                      key={action.id}
                      onClick={() => handleQuickAction(action.href)}
                      className="group relative overflow-hidden rounded-xl border bg-card p-6 text-left transition-all hover:shadow-lg hover:scale-[1.02] active:scale-[0.98]"
                    >
                      <div className={`absolute top-0 right-0 w-24 h-24 ${action.color} rounded-full -translate-y-12 translate-x-12 opacity-10 group-hover:opacity-20 transition-opacity`}></div>
                      <div className="relative z-10">
                        <div className={`inline-flex p-3 rounded-lg ${action.color} mb-4`}>
                          <Icon className="h-6 w-6 text-white" />
                        </div>
                        <h3 className="font-semibold text-lg mb-2">{action.title}</h3>
                        <p className="text-sm text-muted-foreground">{action.description}</p>
                      </div>
                    </button>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          {/* 最近项目 */}
          <Card>
            <CardHeader>
              <CardTitle>最近项目</CardTitle>
              <CardDescription>您最近正在处理的项目</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentProjects.map((project) => (
                  <div
                    key={project.id}
                    className="flex items-center justify-between p-4 rounded-lg border hover:bg-accent/50 transition-colors cursor-pointer"
                    onClick={() => router.push(`/projects/${project.id}`)}
                  >
                    <div className="flex items-center space-x-4">
                      <div className={`w-3 h-3 rounded-full ${getStatusColor(project.status)}`}></div>
                      <div>
                        <h4 className="font-medium">{project.name}</h4>
                        <div className="flex items-center gap-2 mt-1">
                          <Badge variant="outline" className="text-xs">
                            {getTypeLabel(project.type)}
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            <Clock className="inline h-3 w-3 mr-1" />
                            {project.lastUpdated}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="w-32">
                        <Progress value={project.progress} className="h-2" />
                        <p className="text-xs text-muted-foreground text-right mt-1">
                          {project.progress}%
                        </p>
                      </div>
                      <Button variant="ghost" size="sm">
                        继续
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
              <Button 
                variant="outline" 
                className="w-full mt-4"
                onClick={() => router.push("/projects")}
              >
                查看所有项目
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* 右侧：AI模型状态和提示 */}
        <div className="space-y-6">
          {/* AI模型状态 */}
          <Card>
            <CardHeader>
              <CardTitle>AI模型状态</CardTitle>
              <CardDescription>可用模型和性能</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {aiModels.map((model, index) => (
                  <div key={index} className="flex items-center justify-between p-3 rounded-lg border">
                    <div>
                      <div className="font-medium">{model.name}</div>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge 
                          variant={model.type === "local" ? "default" : "secondary"}
                          className="text-xs"
                        >
                          {model.type === "local" ? "本地" : "云端"}
                        </Badge>
                        <Badge 
                          variant="outline" 
                          className="text-xs"
                        >
                          {model.speed}
                        </Badge>
                      </div>
                    </div>
                    <div className={`px-2 py-1 rounded text-xs font-medium ${
                      model.status === "available" 
                        ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300"
                        : "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300"
                    }`}>
                      {model.status === "available" ? "可用" : "维护中"}
                    </div>
                  </div>
                ))}
              </div>
              <Button 
                variant="outline" 
                className="w-full mt-4"
                onClick={() => router.push("/settings/models")}
              >
                管理模型设置
              </Button>
            </CardContent>
          </Card>

          {/* 提示和建议 */}
          <Card>
            <CardHeader>
              <CardTitle>创作提示</CardTitle>
              <CardDescription>提升视频质量的建议</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="p-3 rounded-lg bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800">
                <div className="font-medium text-blue-800 dark:text-blue-300 mb-1">
                  💡 提示词优化
                </div>
                <p className="text-sm text-blue-700 dark:text-blue-400">
                  在提示词中添加具体的时间、地点和情绪描述，可以获得更精确的视频结果。
                </p>
              </div>
              
              <div className="p-3 rounded-lg bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800">
                <div className="font-medium text-green-800 dark:text-green-300 mb-1">
                  ⚡ 快速生成技巧
                </div>
                <p className="text-sm text-green-700 dark:text-green-400">
                  使用本地模型处理批量任务，使用云端API处理高质量单次生成，平衡速度和质量。
                </p>
              </div>
              
              <div className="p-3 rounded-lg bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800">
                <div className="font-medium text-purple-800 dark:text-purple-300 mb-1">
                  🎬 分镜建议
                </div>
                <p className="text-sm text-purple-700 dark:text-purple-400">
                  为每个场景指定镜头类型和摄像机运动，可以让AI生成更专业的视频。
                </p>
              </div>
            </CardContent>
          </Card>

          {/* 资源使用 */}
          <Card>
            <CardHeader>
              <CardTitle>资源使用</CardTitle>
              <CardDescription>本月使用情况</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>视频生成</span>
                    <span>24/50 次</span>
                  </div>
                  <Progress value={48} className="h-2" />
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>剧本生成</span>
                    <span>18/30 次</span>
                  </div>
                  <Progress value={60} className="h-2" />
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>存储空间</span>
                    <span>2.4/10 GB</span>
                  </div>
                  <Progress value={24} className="h-2" />
                </div>
              </div>
              <Button 
                variant="outline" 
                className="w-full mt-4"
                onClick={() => router.push("/billing")}
              >
                升级套餐
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* 底部：活动时间线 */}
      <Card>
        <CardHeader>
          <CardTitle>最近活动</CardTitle>
          <CardDescription>您的创作活动时间线</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[
              { time: "今天 10:30", action: "完成了", item: "产品演示视频", type: "video" },
              { time: "今天 09:15", action: "生成了", item: "社交媒体剧本", type: "script" },
              { time: "昨天 16:45", action: "开始了", item: "新广告项目", type: "project" },
              { time: "昨天 14:20", action: "分享了", item: "教育视频", type: "share" },
            ].map((activity, index) => (
              <div key={index} className="flex items-center">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                  {activity.type === "video" && <Video className="h-4 w-4 text-primary" />}
                  {activity.type === "script" && <FileText className="h-4 w-4 text-primary" />}
                  {activity.type === "project" && <Users className="h-4 w-4 text-primary" />}
                  {activity.type === "share" && <PlayCircle className="h-4 w-4 text-primary" />}
                </div>
                <div className="ml-4">
                  <p className="text-sm">
                    <span className="font-medium">{activity.time}</span>
                    <span className="text-muted-foreground"> - {activity.action} </span>
                    <span className="font-medium">{activity.item}</span>
                  </p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
