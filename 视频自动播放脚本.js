// ==UserScript==
// @name         视频自动播放循环脚本
// @namespace    http://tampermonkey.net/
// @version      2025-10-14
// @description  自动播放视频并循环，每30秒模拟用户活动防止超时，每2分钟自动刷新页面
// @author       You
// @match        https://labsafetest.uestc.edu.cn/redir.php*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=uestc.edu.cn
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    console.log('[视频脚本] 脚本已加载');

    // 查找并设置视频的函数
    function setupVideo() {
        const video = document.querySelector('video');
        
        if (video) {
            console.log('[视频脚本] 找到视频元素');
            
            // 设置视频属性
            video.autoplay = true;
            video.loop = true;
            video.muted = true; // 自动静音播放
            
            // 强制播放视频的函数
            function forcePlay() {
                if (video.paused) {
                    console.log('[视频脚本] 检测到视频暂停，尝试播放');
                    video.play().then(() => {
                        console.log('[视频脚本] 视频开始播放');
                    }).catch(err => {
                        console.log('[视频脚本] 播放失败:', err);
                    });
                }
            }
            
            // 立即尝试播放
            forcePlay();
            
            // 每隔0.5秒检查一次，如果暂停就播放
            const playInterval = setInterval(forcePlay, 500);
            
            // 5秒后停止频繁检查，改为监听事件
            setTimeout(() => {
                clearInterval(playInterval);
                console.log('[视频脚本] 停止频繁检查，切换到事件监听模式');
            }, 5000);
            
            // 监听暂停事件，立即恢复播放
            video.addEventListener('pause', function() {
                console.log('[视频脚本] 检测到暂停事件，立即恢复播放');
                setTimeout(() => {
                    video.play();
                }, 100);
            });
            
            // 监听视频结束事件，确保循环播放
            video.addEventListener('ended', function() {
                console.log('[视频脚本] 视频播放完毕，重新播放');
                video.currentTime = 0;
                video.play();
            });
            
            // 监听加载完成事件
            video.addEventListener('loadeddata', function() {
                console.log('[视频脚本] 视频数据加载完成，尝试播放');
                video.play();
            });
            
            // 尝试点击页面上的播放按钮（如果有的话）
            setTimeout(() => {
                // 查找可能的播放按钮
                const playButton = document.querySelector('.vjs-big-play-button') || 
                                 document.querySelector('[aria-label*="播放"]') ||
                                 document.querySelector('button[class*="play"]');
                if (playButton) {
                    console.log('[视频脚本] 找到播放按钮，自动点击');
                    playButton.click();
                }
            }, 500);
            
            return true;
        }
        
        return false;
    }

    // 模拟用户活动的函数
    function simulateUserActivity() {
        console.log('[视频脚本] 模拟用户活动，防止超时');
        
        // 1. 模拟鼠标移动事件
        const moveEvent = new MouseEvent('mousemove', {
            view: window,
            bubbles: true,
            cancelable: true,
            clientX: Math.random() * window.innerWidth,
            clientY: Math.random() * window.innerHeight
        });
        document.dispatchEvent(moveEvent);
        document.body.dispatchEvent(moveEvent);
        
        // 2. 模拟鼠标悬停事件
        const overEvent = new MouseEvent('mouseover', {
            view: window,
            bubbles: true,
            cancelable: true
        });
        document.body.dispatchEvent(overEvent);
        
        // 3. 模拟点击事件
        const clickEvent = new MouseEvent('click', {
            view: window,
            bubbles: true,
            cancelable: true,
            clientX: Math.random() * window.innerWidth,
            clientY: Math.random() * window.innerHeight
        });
        document.body.dispatchEvent(clickEvent);
        
        // 4. 模拟键盘活动（按下并释放一个不可见的键）
        const keydownEvent = new KeyboardEvent('keydown', {
            bubbles: true,
            cancelable: true,
            key: 'Shift'
        });
        const keyupEvent = new KeyboardEvent('keyup', {
            bubbles: true,
            cancelable: true,
            key: 'Shift'
        });
        document.dispatchEvent(keydownEvent);
        document.dispatchEvent(keyupEvent);
        
        // 5. 触发页面滚动事件
        const scrollEvent = new Event('scroll', {
            bubbles: true,
            cancelable: true
        });
        window.dispatchEvent(scrollEvent);
        
        // 6. 触发焦点事件
        const focusEvent = new FocusEvent('focus', {
            bubbles: true,
            cancelable: true
        });
        window.dispatchEvent(focusEvent);
    }

    // 等待页面加载完成
    function init() {
        // 尝试立即查找视频
        if (setupVideo()) {
            console.log('[视频脚本] 视频设置成功');
        } else {
            console.log('[视频脚本] 视频元素未找到，等待加载...');
            
            // 如果没找到，使用MutationObserver监听DOM变化
            const observer = new MutationObserver(function(mutations) {
                if (setupVideo()) {
                    console.log('[视频脚本] 视频设置成功');
                    observer.disconnect();
                }
            });
            
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
            
            // 10秒后停止观察
            setTimeout(() => {
                observer.disconnect();
                console.log('[视频脚本] 停止监听DOM变化');
            }, 10000);
        }
        
        // 多次尝试点击播放按钮，确保成功
        [1000, 2000, 3000, 5000].forEach(delay => {
            setTimeout(() => {
                const video = document.querySelector('video');
                if (video && video.paused) {
                    console.log('[视频脚本] 定时检查：视频仍暂停，尝试播放');
                    video.play();
                }
            }, delay);
        });
        
        // 立即执行一次用户活动模拟
        setTimeout(simulateUserActivity, 3000);
        
        // 设置每30秒模拟一次用户活动（更频繁地防止超时）
        setInterval(simulateUserActivity, 30000); // 30000毫秒 = 30秒
        console.log('[视频脚本] 已设置每30秒自动模拟用户活动');
        
        // 额外增加：每10秒检查一次视频是否暂停
        setInterval(() => {
            const video = document.querySelector('video');
            if (video && video.paused) {
                console.log('[视频脚本] 定期检查：视频暂停，立即播放');
                video.play();
            }
        }, 10000); // 10000毫秒 = 10秒
        console.log('[视频脚本] 已设置每10秒检查视频播放状态');
        
        // 设置定时刷新页面，防止长时间停留
        const refreshInterval = 2 * 60 * 1000; // 2分钟 = 120000毫秒
        setTimeout(() => {
            console.log('[视频脚本] 2分钟已到，自动刷新页面');
            location.reload();
        }, refreshInterval);
        console.log('[视频脚本] 已设置2分钟后自动刷新页面');
    }

    // 当DOM准备好时执行
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // 页面完全加载后再次尝试
    window.addEventListener('load', function() {
        console.log('[视频脚本] 页面完全加载');
        setupVideo();
    });

})();

