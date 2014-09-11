# -*- coding:utf-8 -*-
import re
def Ubb2Html(content):
	#以下是将html标签转为ubb标签
	pattern = re.compile( '\[color=([\s\S]+?)\]([\s\S]+?)\[/color\]',re.I)#颜色
	content = pattern.sub(r'<span style="color:\1">\2</span>',content)
	
	pattern = re.compile( '\[size=([\s\S]+?)\]([\s\S]+?)\[/size\]',re.I)#字体
	content = pattern.sub(r'<span style="font-size:\1">\2</span>',content)
	
	pattern = re.compile( '\[b]([\s\S]+?)\[/b\]',re.I)#粗体
	content = pattern.sub(r'<strong >\1</strong>',content)	
	
	pattern = re.compile( '\[i]([\s\S]+?)\[/i\]',re.I)#斜体
	content = pattern.sub(r'<em >\1</em>',content)	
	
	pattern = re.compile( '\[u]([\s\S]+?)\[/u\]',re.I)#下滑线
	content = pattern.sub(r'<span style="text-decoration: underline" >\1</span>',content)
	
	pattern = re.compile( '\[del]([\s\S]+?)\[/del\]',re.I)#删除线
	content = pattern.sub(r'<span style="text-decoration: line-through" >\1</span>',content)
	
	pattern = re.compile( '\[align=left]([\s\S]+?)\[/align\]',re.I)#居左显示
	content = pattern.sub(r'<div style="text-align: left" >\1</div>',content)

	pattern = re.compile( '\[align=right]([\s\S]+?)\[/align\]',re.I)#居右显示
	content = pattern.sub(r'<div style="text-align: right" >\1</div>',content)
	
	pattern = re.compile( '\[align=center]([\s\S]+?)\[/align\]',re.I)#居右显示
	content = pattern.sub(r'<div style="text-align: center" >\1</div>',content)
	
	pattern = re.compile( '\[url=([\s\S]+?)\]([\s\S]+?)\[/url\]',re.I)#链接
	content = pattern.sub(r'<a href="\1" target="_blank">\2</a>',content)
	
	pattern = re.compile( '\[email=([\s\S]+?)\]([\s\S]+?)\[/email\]',re.I)#email
	content = pattern.sub(r'<a href="mailto:\1">\2</a>',content)
	
	pattern = re.compile( '\[img=([\s\S]+?)\]([\s\S]+?)\[/img\]',re.I)#图片
	content = pattern.sub(r'<img src="\1" alt="\2"/>',content)
		
	#以下是将html转义字符转为普通字符
	return content

