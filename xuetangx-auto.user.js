// ==UserScript==
// @name         学堂在线刷课 (1.0x倍速版)
// @namespace    http://tampermonkey.net/
// @version      0.7.1
// @description  该脚本可以完成学堂在线课程中的视频以及图文，自动跳过课后习题和讨论题，并将视频速度锁定在1.0x。新增：严格的视频完整播放检测，等待学堂在线平台确认完成状态（最多10秒），10秒跳转冷却机制，防止重复调用，确保每次只跳转一个视频并完整播放。
// @match        https://www.xuetangx.com/*
// @require      https://code.jquery.com/jquery-3.7.1.js
// @icon         data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==
// @grant        none
// @license      GNU GPLv3
// @downloadURL https://update.greasyfork.org/scripts/476168/%E5%AD%A6%E5%A0%82%E5%9C%A8%E7%BA%BF%E5%88%B7%E8%AF%BE.user.js
// @updateURL https://update.greasyfork.org/scripts/476168/%E5%AD%A6%E5%A0%82%E5%9C%A8%E7%BA%BF%E5%88%B7%E8%AF%BE.meta.js
// ==/UserScript==

(function () {
    'use strict';
    
    console.log('========================================');
    console.log('学堂在线自动刷课脚本已启动 (1.0x倍速版)');
    console.log('版本: 0.7.1');
    console.log('功能: 严格视频完整播放检测 + 平台完成状态确认 + 10秒跳转冷却');
    console.log('跳转冷却时间: 10 秒');
    console.log('平台状态等待: 最多 10 秒');
    console.log('提示: 如需清除已完成视频记录，请在控制台执行:');
    console.log('localStorage.removeItem("xuetangx_completed_videos")');
    console.log('========================================');
    
    // ========== 视频完成状态管理 ==========
    
    // 获取当前视频的唯一标识
    function getVideoId() {
        // 使用URL路径作为视频的唯一标识
        let path = window.location.pathname + window.location.search;
        return path;
    }
    
    // 检查视频是否已完成
    function isVideoCompleted(videoId) {
        try {
            let completedVideos = JSON.parse(localStorage.getItem('xuetangx_completed_videos') || '{}');
            return completedVideos[videoId] === true;
        } catch (e) {
            console.error("读取已完成视频记录失败:", e);
            return false;
        }
    }
    
    // 标记视频为已完成
    function markVideoAsCompleted(videoId) {
        try {
            let completedVideos = JSON.parse(localStorage.getItem('xuetangx_completed_videos') || '{}');
            completedVideos[videoId] = true;
            localStorage.setItem('xuetangx_completed_videos', JSON.stringify(completedVideos));
            console.log("✓ 视频已标记为完成:", videoId);
        } catch (e) {
            console.error("保存已完成视频记录失败:", e);
        }
    }
    
    // 检测学堂在线平台是否标记当前视频为完成
    function isPlatformMarkedComplete() {
        try {
            console.log("🔍 开始检测平台完成状态...");
            
            // 方法1: 检查视频进度百分比（最简单直接）
            let video = $("video")[0];
            if (video && video.duration > 0) {
                let progress = (video.currentTime / video.duration) * 100;
                console.log("视频播放进度:", progress.toFixed(2) + "%");
                
                // 如果播放进度 >= 99.5%，认为平台应该已标记完成
                if (progress >= 99.5) {
                    console.log("✓ 视频播放进度已达到99.5%以上");
                    // 再等待2秒让平台同步状态
                    return true;
                }
            }
            
            // 方法2: 检查左侧目录当前节点的完成状态
            // 查找所有可能的当前播放节点选择器
            let possibleSelectors = [
                '.cur_play',
                '.playing', 
                '.active',
                '.current',
                '[class*="active"]',
                '[class*="playing"]'
            ];
            
            for (let selector of possibleSelectors) {
                let nodes = $(selector);
                console.log("检查选择器:", selector, "找到节点数:", nodes.length);
                
                if (nodes.length > 0) {
                    nodes.each(function() {
                        let node = $(this);
                        let classes = node.attr('class') || '';
                        let hasFinished = classes.includes('finished') || 
                                        classes.includes('completed') || 
                                        classes.includes('done');
                        
                        if (hasFinished) {
                            console.log("✓ 找到完成标记，class:", classes);
                            return true;
                        }
                    });
                }
            }
            
            console.log("❌ 未检测到平台完成标记");
            return false;
        } catch (e) {
            console.error("检测平台完成状态失败:", e);
            return false;
        }
    }
    
    // 等待学堂在线平台标记视频完成
    function waitForPlatformComplete(callback, maxWaitTime = 10000) {
        // 防止重复调用
        if (isWaitingForPlatform) {
            console.log("⏸ 已经在等待平台确认中，忽略重复调用");
            return;
        }
        
        isWaitingForPlatform = true;
        console.log("⏳ 等待学堂在线平台标记视频完成...");
        let startTime = Date.now();
        let checkInterval = setInterval(() => {
            let elapsedTime = Date.now() - startTime;
            
            if (isPlatformMarkedComplete()) {
                clearInterval(checkInterval);
                isWaitingForPlatform = false;
                console.log("✓ 平台已确认视频完成，准备跳转");
                callback(true);
                return;
            }
            
            // 超时处理
            if (elapsedTime >= maxWaitTime) {
                clearInterval(checkInterval);
                isWaitingForPlatform = false;
                console.warn("⚠ 等待平台标记超时(" + (maxWaitTime/1000) + "秒)，强制跳转");
                callback(false);
                return;
            }
            
            // 每5秒输出一次等待状态
            if (elapsedTime % 5000 < 1000) {
                console.log("⏳ 等待中... 已等待", Math.floor(elapsedTime/1000), "秒");
            }
        }, 1000); // 每秒检查一次
    }
    
    // ========== 自动刷课相关 ==========
    
    // 自动开始刷课
    let autoInterval;
    
    // 跳转控制变量
    let isJumping = false; // 跳转锁，防止重复跳转
    let lastJumpTime = 0; // 上次跳转的时间戳
    const JUMP_COOLDOWN = 10000; // 跳转冷却时间：10秒
    let isWaitingForPlatform = false; // 是否正在等待平台确认
    
    // 等待页面加载完成后自动开始
    setTimeout(function() {
        startAutoClass();
    }, 3000);

    // 自动开始刷课函数
    function startAutoClass() {
        console.log('开始自动刷课');
        clearInterval(autoInterval);
        autoInterval = setInterval(startClass, 2000);
    }

    // 统一的跳转函数，带冷却控制
    function jumpToNext(reason) {
        let currentTime = Date.now();
        
        // 检查是否在冷却期内
        if (isJumping || (currentTime - lastJumpTime < JUMP_COOLDOWN)) {
            console.log("⏸ 跳转冷却中，忽略本次跳转请求");
            return false;
        }
        
        isJumping = true;
        lastJumpTime = currentTime;
        
        console.log("========================================");
        console.log("🔄 准备跳转到下一节");
        console.log("跳转原因:", reason);
        console.log("========================================");
        
        $(".next").click();
        
        // 10秒后解除跳转锁
        setTimeout(() => {
            isJumping = false;
            console.log("✓ 跳转冷却结束，可以继续检测");
        }, JUMP_COOLDOWN);
        
        return true;
    }

    // 视频脚本
    function startVideo() {
        // 如果正在跳转中或等待平台确认中，暂停检测
        if (isJumping) {
            console.log("⏸ 正在跳转中，暂停视频检测...");
            return;
        }
        
        if (isWaitingForPlatform) {
            console.log("⏸ 正在等待平台确认，暂停视频检测...");
            return;
        }
        
        let video = $("video")[0];
        if (!video) {
            console.log("未找到视频元素，等待加载...");
            return;
        }

        // 获取当前视频ID
        let videoId = getVideoId();
        console.log("当前视频ID:", videoId);
        
        // 检查当前视频是否已完成
        if (isVideoCompleted(videoId)) {
            console.log("⚠ 此视频已完成");
            jumpToNext("视频已完成");
            return;
        }

        // 为视频添加ended事件监听（只添加一次）
        if (!video.hasAttribute('data-auto-listener')) {
            video.setAttribute('data-auto-listener', 'true');
            // 使用立即执行函数确保videoId被正确捕获
            (function(currentVideoId) {
                video.addEventListener('ended', function() {
                    console.log("========================================");
                    console.log("✓ 视频ended事件触发，视频已播放完成");
                    console.log("完成的视频ID:", currentVideoId);
                    console.log("========================================");
                    
                    // 等待学堂在线平台标记完成
                    waitForPlatformComplete((platformConfirmed) => {
                        markVideoAsCompleted(currentVideoId);
                        if (platformConfirmed) {
                            jumpToNext("ended事件触发 + 平台已确认");
                        } else {
                            jumpToNext("ended事件触发 + 平台超时");
                        }
                    }, 10000); // 最多等待10秒
                });
            })(videoId);
            console.log("✓ 已为视频添加ended事件监听器");
        }

        let staNow = $(".play-btn-tip");
        if (staNow.text() == "播放") {
            $(".xt_video_player_mask").click();
            console.log("点击播放按钮");
        }

        let c = video.currentTime;
        let d = video.duration;

        if (d && !isNaN(d)) {
            let percentage = ((c/d)*100).toFixed(1);
            let remainingTime = d - c;
            
            console.log(`视频进度: ${c.toFixed(1)}/${d.toFixed(1)}秒 (${percentage}%) 剩余: ${remainingTime.toFixed(1)}秒`);

            //不想关闭声音可以把此行代码删掉
            soundClose();
            speed(); // 调用修改后的speed函数

            // 严格检测：剩余时间小于1秒时提示即将结束
            if (remainingTime > 0 && remainingTime < 1.0) {
                console.log(`⚠ 视频即将结束，剩余${remainingTime.toFixed(2)}秒`);
            }

            // 只有在极端情况下（ended事件未触发但已播放完）才手动跳转
            // 必须满足：当前时间 >= 总时长 - 0.5秒，且视频已经开始播放
            if (c >= d - 0.5 && c > 0 && d > 0) {
                let isMarked = isVideoCompleted(videoId);
                if (!isMarked) {
                    console.log("✓ 检测到视频已播放至末尾（备用检测）");
                    console.log(`本节观看完成度: ${percentage}%`);
                    
                    // 等待学堂在线平台标记完成
                    waitForPlatformComplete((platformConfirmed) => {
                        markVideoAsCompleted(videoId);
                        if (platformConfirmed) {
                            jumpToNext("视频播放完成（备用检测） + 平台已确认");
                        } else {
                            jumpToNext("视频播放完成（备用检测） + 平台超时");
                        }
                    }, 10000); // 最多等待10秒
                }
            }
        } else {
            console.log("视频时长未加载，等待...");
        }
    }

    //关闭视频声音
    function soundClose() {
        let sound = $(".xt_video_player_common_icon_muted");
        if (sound.length == 0) {
            $(".xt_video_player_common_icon").click();
        }
    }
    
    //播放速度锁定1.0
    function speed() {
        // 找到当前显示速度的元素，检查是否已经是1.0x，避免重复点击
        let currentSpeedLabel = $(".xt_video_player_common_label");
        if (currentSpeedLabel.text().trim() === "1.0x") {
            return; // 如果已经是1.0x，则不做任何操作
        }
        
        // 找到包含所有速度选项的列表元素
        let speedList = $(".xt_video_player_common_list");
        
        if (speedList.length > 0) {
            // 从列表中筛选出文本内容为 "1.0x" 的那个选项
            let speedOption1x = speedList.children().filter(function() {
                // 使用 .trim() 去除可能的空格，确保精确匹配
                return $(this).text().trim() === "1.0x";
            });

            // 如果成功找到了 "1.0x" 选项，就点击它
            if (speedOption1x.length > 0) {
                speedOption1x.click();
                console.log("播放速度已设置为 1.0x");
            }
        }
    }

    // 刷附件
    let word = function () {
        let next = document.querySelector('.btnCon button');
        let click = new Event('mouseup');
        next.dispatchEvent(click);
        if ($(next).text() == '我已看完') {
            $('.next').click()
        }
    }

    // 检测是否为课后习题或讨论题
    function isHomeworkOrDiscussion() {
        // 检测课后习题关键词
        let homeworkIndicators = [
            '课后习题',
            '课后练习',
            '课后作业',
            '章节练习',
            '习题',
            '练习',
            '作业',
            '测验',
            '考试',
            'quiz'
        ];

        // 检测讨论题关键词
        let discussionIndicators = [
            '讨论题',
            '课堂讨论',
            '互动讨论',
            '论坛讨论',
            '讨论',
            'discussion',
            '交流',
            '分享',
            '思考题'
        ];

        // 获取页面的多个信息源
        let sectionTitle = $('.t1').eq(0).text() || '';
        let breadcrumb = $('.breadcrumb').text() || '';
        let pageTitle = document.title || '';
        let mainTitle = $('h1').text() || '';
        let subTitle = $('h2').text() || '';
        let contentArea = $('.content-area').text() || '';

        // 合并所有文本进行检查
        let allText = (sectionTitle + ' ' + breadcrumb + ' ' + pageTitle + ' ' + mainTitle + ' ' + subTitle + ' ' + contentArea).toLowerCase();

        console.log("检测文本内容:", allText);

        let isHomework = homeworkIndicators.some(indicator => {
            let found = allText.includes(indicator.toLowerCase());
            if (found) console.log("匹配到课后习题关键词:", indicator);
            return found;
        });

        let isDiscussion = discussionIndicators.some(indicator => {
            let found = allText.includes(indicator.toLowerCase());
            if (found) console.log("匹配到讨论题关键词:", indicator);
            return found;
        });

        let result = isHomework || isDiscussion;
        console.log("是否为课后习题或讨论题:", result);

        return result;
    }

    // 额外的检测方法 - 通过URL和DOM结构
    function isSkippablePage() {
        // 检查URL
        let currentUrl = window.location.href.toLowerCase();
        let urlKeywords = ['homework', 'discussion', 'quiz', 'exercise', 'practice'];
        let urlMatch = urlKeywords.some(keyword => currentUrl.includes(keyword));

        // 检查是否有特定的DOM结构
        let hasDiscussionForm = $('.discussion-form').length > 0 || $('.forum-form').length > 0;
        let hasHomeworkForm = $('.homework-form').length > 0 || $('.exercise-form').length > 0;
        let hasQuizForm = $('.quiz-form').length > 0;

        // 检查是否有提交按钮相关的文本
        let submitButtons = $('button, input[type="submit"], .btn').filter(function() {
            let text = $(this).text().toLowerCase();
            return text.includes('提交') || text.includes('发布') || text.includes('回复') || text.includes('submit');
        });

        let hasSubmitButton = submitButtons.length > 0;

        return urlMatch || hasDiscussionForm || hasHomeworkForm || hasQuizForm || hasSubmitButton;
    }

    // 开始刷课主函数
    function startClass() {
        // 获取页面类型
        let types = $('.t1').eq(0).text();
        console.log("当前页面类型:", types);

        // 首先处理视频和附件
        if (types == '视频') {
            console.log("检测到视频页面，开始播放");
            startVideo();
            return;
        } else if (types == '附件') {
            console.log("检测到附件页面，开始处理");
            word();
            return;
        }

        // 多重检测是否为课后习题或讨论题
        let shouldSkip = isHomeworkOrDiscussion() || isSkippablePage();

        if (shouldSkip) {
            console.log("检测到课后习题或讨论题，自动跳过");
            $('.next').click();
            return;
        }

        // 检查是否有答题界面
        if ($('.answerList').length != 0) {
            console.log("检测到题目页面，自动跳过");
            $('.next').click();
            return;
        }

        // 如果页面类型为空或未知，也尝试跳过
        if (!types || types.trim() === '') {
            console.log("页面类型为空，可能是习题或讨论页面，尝试跳过");
            $('.next').click();
            return;
        }

        // 如果都不是，等待一下再检查
        console.log("页面类型未确定，等待加载...");
    }

})();
