// ==UserScript==
// @name         学堂在线刷课
// @namespace    http://tampermonkey.net/
// @version      0.4.0
// @description  该脚本可以完成学堂在线课程中的视频以及图文，自动跳过课后习题和讨论题
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
    
    console.log('学堂在线自动刷课脚本已启动');
    
    // 自动开始刷课
    let autoInterval;
    
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

    // 视频脚本
    function startVideo() {
        let video = $("video")[0];
        if (!video) {
            console.log("未找到视频元素，等待加载...");
            return;
        }

        let staNow = $(".play-btn-tip");
        if (staNow.text() == "播放") {
            $(".xt_video_player_mask").click();
            console.log("点击播放按钮");
        }

        let c = video.currentTime;
        let d = video.duration;

        if (d && !isNaN(d)) {
            console.log(`视频进度: ${c}/${d} (${((c/d)*100).toFixed(1)}%)`);

            //不想关闭声音可以把此行代码删掉
            soundClose();
            speed();

            //视频播放进度达到100%跳转下一节视频
            if ((c / d) >= 1.0 || c >= d) {
                $(".next").click();
                console.log("视频播放完成，跳转到下一节");
                console.log("本节观看百分比" + ((c/d)*100).toFixed(1) + "%");
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
    
    //播放速度2.0
    function speed() {
        let speed = $(".xt_video_player_common_list");
        let speedChild = speed.children()[0];
        if (speedChild) {
            speedChild.click();
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
