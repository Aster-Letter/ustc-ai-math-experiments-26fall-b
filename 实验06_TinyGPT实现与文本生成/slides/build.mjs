import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';

import {fileURLToPath,pathToFileURL} from 'node:url';
const nodeModules=process.env.RUNTIME_NODE_MODULES;
if(!nodeModules) throw new Error('Set RUNTIME_NODE_MODULES to the Artifact Tool package directory.');
const runtimeRequire=createRequire(path.join(nodeModules,'entry.js'));
const {Presentation,PresentationFile}=await import(pathToFileURL(runtimeRequire.resolve('@oai/artifact-tool')).href);
const SKILL=process.env.PRESENTATION_SKILL_DIR;
if(!SKILL) throw new Error('Set PRESENTATION_SKILL_DIR to the presentations skill directory.');
const {applyPresentationChartFont,finalizePresentation}=await import(pathToFileURL(path.join(SKILL,'container_tools/artifact_tool_utils.mjs')).href);
const BASE=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const BUILD=path.join(BASE,'tmp','slides-build-'+Date.now()), OUT=path.join(BASE,'slides');
const FONT='Noto Sans CJK SC',MONO='DejaVu Sans Mono';
const C={ink:'#14263D',blue:'#216C9C',cyan:'#078C91',amber:'#AA671C',red:'#AE3C37',paper:'#FAFBFD',pale:'#EAF2F8',warm:'#FFF2DB',gray:'#596B7C',line:'#CAD7E2'};
const P=Presentation.create({slideSize:{width:1280,height:720}});
const source='实验06_实验讲义.tex；code/student.py';
const results='teacher/pro5k-20261029/ccpc-five/：history.csv、run.json、test_metrics.json、generation_audit.json、sample-t08.txt。预跑设备：pro5k；107平台的设备与耗时由学生作业日志记录。';
const titles=[],geometries=[];
function text(s,str,x,y,w,h,size=28,color=C.ink,bold=false,font=FONT){let a=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});a.text=str;a.text.style={fontSize:size,typeface:font,fontFamily:font,color,bold,autoFit:'none',verticalAlignment:'top',insets:0};geometries.push({slide:P.slides.items.length,text:typeof str==='string'?str:'rich',x,y,w,h,size,bold,font});return a;}
function rect(s,x,y,w,h,fill=C.pale,stroke='none'){return s.shapes.add({geometry:'rect',position:{left:x,top:y,width:w,height:h},fill,line:{fill:stroke,width:stroke==='none'?0:1}});}
function box(s,str,x,y,w,h,fill=C.pale,size=28){let a=rect(s,x,y,w,h,fill,C.line);a.text=str;a.text.style={fontSize:size,typeface:FONT,fontFamily:FONT,color:C.ink,alignment:'center',verticalAlignment:'middle',insets:8};return a;}
function link(s,a,b,from='right',to='left',color=C.blue){return s.shapes.connect(a,b,{kind:'straight',fromSide:from,toSide:to,line:{fill:color,width:2.4},tail:{type:'triangle',width:'sm',length:'sm'}});}
function slide(title,sub='',notes=source){let s=P.slides.add();s.background.fill=C.paper;titles.push(title);text(s,title,56,34,1168,66,43,C.ink,true);if(sub)text(s,sub,58,108,1164,58,24,C.gray);text(s,String(titles.length).padStart(2,'0'),1176,677,48,24,17,C.gray);s.speakerNotes.text=notes;return s;}
function note(s,str){text(s,str,60,617,1150,60,23,C.gray);}
function code(s,str,x=660,y=205,w=555,h=330,size=25){rect(s,x-16,y-15,w+32,h+30,'#172B43');return text(s,str,x,y,w,h,size,'#F4F7FB',false,MONO);}
const formulaManifest=JSON.parse(await fs.readFile(path.join(OUT,'assets/formulas/manifest.json'),'utf8'));
const formulaBytes=Object.fromEntries(await Promise.all(Object.keys(formulaManifest).map(async key=>[key,new Uint8Array(await fs.readFile(path.join(OUT,'assets/formulas',key+'.png')))])));
const formulaAudit=[];
function math(s,key,x,y,w=540,size=34,number=null,align='left',maxH=150){
  const f=formulaManifest[key];
  if(!f)throw new Error('Missing rendered LaTeX formula: '+key);
  const available=w-(number?108:0), scale=Math.min(size/f.fontPx,available/f.width,maxH/f.height);
  const width=f.width*scale,height=f.height*scale;
  const left=x+(align==='center'?(available-width)/2:0);
  const img=s.images.add({blob:formulaBytes[key],contentType:'image/png',alt:f.latex,fit:'contain',position:{left,top:y,width,height}});
  if(number)text(s,'('+number+')',x+w-93,y+Math.max(0,(height-30)/2),93,30,20,C.gray);
  formulaAudit.push({slide:P.slides.items.length,key,fontPx:scale*f.fontPx,x:left,y,width,height,number});
  return img;
}
function mathBox(s,label,key,x,y,w,h,fill=C.pale,size=28){
  const a=rect(s,x,y,w,h,fill,C.line);
  if(label){let t=text(s,label,x+8,y+12,w-16,40,28);t.text.style={fontSize:28,fontFamily:FONT,typeface:FONT,color:C.ink,alignment:'center',insets:0};}
  const f=formulaManifest[key],availableH=label?h-55:h-16;
  const scale=Math.min(size/f.fontPx,(w-20)/f.width,availableH/f.height);
  const top=label?y+48+(availableH-f.height*scale)/2:y+(h-f.height*scale)/2;
  math(s,key,x+10,top,w-20,size,null,'center',availableH);
  return a;
}
const eqs={
'pθ(x₂,…,xₜ₊₁ | x₁) = ∏ᵢ₌₁ᵀ pθ(xᵢ₊₁ | x≤ᵢ)':['autoregressive','5.1.1'],
'S = QKᵀ / √k':['attention_scores','3.2.1'],
'P = Softmax(S + M)':['attention_weights','3.2.2'],
'O = PV':['attention_output','3.2.3'],
'ℒB = −(1/BT) ∑ₙ ∑ᵢ log pθ(yᵢ⁽ⁿ⁾ | x≤ᵢ⁽ⁿ⁾)':['batch_loss','5.1.2'],
'pᵥ(τ) = exp(zᵥ/τ) / ∑ᵣ exp(zᵣ/τ)':['sampling_distribution','7.1.1'],
'2Vd + Td + L(12d² + 13d) + 2d':['parameter_count','A.1.1'],
'ℒpos = −log pᵧ = −zᵧ + log ∑ᵣ exp(zᵣ)':['position_loss','5.2.1'],
'∂ℒpos / ∂zᵥ = −1{v=y} + exp(zᵥ)/∑ᵣ exp(zᵣ)':['position_gradient_expanded','5.2.2'],
'∂ℒpos / ∂zᵥ = pᵥ − 1{v=y}':['position_gradient','5.2.3'],
'(1,2,3)  遮挡后  (1,2,−∞)':['mask_scores_example',null]};
function formula(s,str,x,y,w=540,size=34){const [key,number]=eqs[str];return math(s,key,x,y,w,size,number);}

function table(s,vals,x=60,y=190,w=1160,h=340,widths=null,size=25){let t=s.tables.add({rows:vals.length,columns:vals[0].length,left:x,top:y,width:w,height:h,values:vals,...(widths?{columnWidths:widths}:{})});t.borders.assign({fill:C.line,width:1,style:'solid'});for(let r=0;r<vals.length;r++)for(let c=0;c<vals[0].length;c++){let cell=t.getCell(r,c);cell.fill=r===0?C.ink:r%2? '#FFFFFF':C.pale;cell.text.style={fontFamily:FONT,typeface:FONT,fontSize:size,color:r===0?'#FFFFFF':C.ink,bold:r===0,verticalAlignment:'middle',insets:12};}return t;}
function chart(s,type,categories,series,x,y,w,h,extra={}){let c=s.charts.add(type,{position:{left:x,top:y,width:w,height:h},categories,series,lineOptions:{smooth:false},hasLegend:series.length>1,legend:{position:'bottom',textStyle:{fontSize:24}},chartFill:C.paper,chartLine:{fill:'none',width:0},plotAreaFill:C.paper,xAxis:{textStyle:{fontSize:22},line:{fill:C.line,width:1}},yAxis:{textStyle:{fontSize:22},majorGridlines:{fill:C.line,width:1}},...extra});applyPresentationChartFont(c,{fontFamily:FONT});return c;}
function cells(s,chars,x,y,size=64,highlight=-1){return [...chars].map((c,i)=>box(s,c,x+i*(size+10),y,size,size,i===highlight?C.warm:C.pale,32));}
const csv=async f=>{let [head,...lines]=(await fs.readFile(f,'utf8')).trim().split('\n');let names=head.split(',');return lines.map(l=>Object.fromEntries(l.split(',').map((v,i)=>[names[i],Number(v)])));};
const hist=await csv(path.join(OUT,'data/ccpc-five-history.csv'));
// 01
{let s=P.slides.add();s.background.fill=C.ink;titles.push('实验六  从零实现 TinyGPT');text(s,'人工智能数学原理与算法',68,58,1100,45,28,'#D3E7F5');text(s,'从零实现 TinyGPT\n生成五言诗',66,166,1100,180,64,'#FFFFFF',true);text(s,'Generative Pre-trained Transformer\n生成式预训练 Transformer',72,375,1000,80,27,'#B9DDE6');text(s,'主讲：钟志诚    整理：曾有成、冯筱璐\n中国科学技术大学 人工智能与数据科学学院',72,524,1120,90,26,'#FFFFFF');text(s,'2026年秋季   3学时 / 135分钟',72,652,1000,30,22,'#B9DDE6');s.speakerNotes.text='定位：第8次Transformer理论课之后的实现实验。代码从随机参数训练，不调用预训练生成接口。封面署名依据课程约定与用户指定。';}
// 02
{
  const s=slide('从判断到生成：典型任务与算法',
    '任务目标、模型结构、生成机制和训练信号，是相互交叉的维度。',
    '表中列出各模型的典型用法。同一结构可服务多种任务：CNN可以组成生成器，BERT可微调做分类；本页列出其掩码预训练任务。条件生成（如翻译）同样学习条件分布，判别式与生成式应结合任务目标和建模对象区分。GPT训练有已知真实前缀，可并行计算各位置，常规生成依次采样词元。本实验每个词元是一个字符。基础GAN的生成器一次前向生成整幅图像，训练同时使用判别器。常规扩散采样需要多步去噪，每步可同时更新各空间位置，步间依次执行；这是一种逐步采样机制，位置并行本身并不决定总体速度。表内公式展示核心计算，完整训练目标见各模型资料。来源：邱锡鹏《神经网络与深度学习》8.4、13.1；https://aclanthology.org/N19-1423/；https://arxiv.org/abs/1706.03762；https://arxiv.org/abs/1406.2661；https://arxiv.org/abs/2006.11239；https://hojonathanho.github.io/diffusion/。');
  const t=table(s,[
    ['模型 / 方法','具体任务','核心表达（示意）','训练与输出方式'],
    ['','判别：图像分类\n图像 → 猫 / 狗','','监督学习\n一次前向得类别'],
    ['','掩码填词\n春风又□江南岸','','自监督填空\n读取左右上下文'],
    ['','生成：诗句续写\n春梦满 → 后续诗句','','自监督下一字预测\n按前缀逐字生成'],
    ['','生成：图像合成\n噪声 → 一张猫图','','对抗训练\n生成器一次前向'],
    ['','生成：图像合成\n噪声 → 一张猫图','','由加噪构造目标\n采样需多次去噪']
  ],60,161,1160,460,[330,230,350,250],24);
  t.cells.block({row:0,column:0,rowCount:6,columnCount:4}).assign({margins:{left:10,right:10,top:0,bottom:0}});
  t.rows[0].height=50;
  for(let c=0;c<4;c++)t.getCell(0,c).text.style={fontSize:24,fontFamily:FONT,typeface:FONT,color:'#FFFFFF',bold:true,verticalAlignment:'middle',insets:{left:12,right:12,top:8,bottom:8}};
  const names=[
    ['CNN','(Convolutional Neural Network)'],
    ['BERT','(Bidirectional Encoder\nRepresentations from Transformers)'],
    ['GPT / 本实验','(Generative Pre-trained Transformer)'],
    ['GAN','(Generative Adversarial Network)'],
    ['扩散模型','Diffusion Model']
  ];
  const formulas=JSON.parse(await fs.readFile(path.join(OUT,'assets/formulas/manifest.json'),'utf8'));
  for(let r=1;r<=5;r++){
    t.rows[r].height=82;
    for(let c=0;c<4;c++){
      const cell=t.getCell(r,c);
      cell.text.style={fontFamily:FONT,typeface:FONT,fontSize:24,color:C.ink,verticalAlignment:'middle',insets:{left:12,right:12,top:3,bottom:3}};
      if(r===3)cell.fill='#E1F1F2';
    }
    t.getCell(r,0).text.style={fontSize:18,fontFamily:FONT,typeface:FONT,color:C.ink,verticalAlignment:'middle',insets:{left:12,right:12,top:3,bottom:3}};
    t.getCell(r,0).value=[
      {runs:[{run:names[r-1][0],style:{fontSize:'26px',bold:true,color:r===3?C.cyan:C.ink,typeface:FONT}}]},
      {runs:[{run:names[r-1][1],style:{fontSize:'18px',color:C.gray,typeface:FONT}}]}
    ];
    const key=['cnn','bert','gpt','gan','diffusion'][r-1], f=formulas[key];
    const scale=Math.min(1.14,320/f.width,60/f.height), w=f.width*scale,h=f.height*scale;
    math(s,key,620,211+(r-1)*82+(82-h)/2,350,f.fontPx*scale,null,'center',60);
  }
  text(s,'p表示概率，θ为模型参数，G为生成器。竖线表示“给定”，箭头表示生成过程。',60,634,1150,28,20,C.gray);
  text(s,'本实验训练可并行，采样逐字。扩散通常逐步去噪，每步更新整幅图像。',60,669,1100,33,23,C.blue);
}
// 03
{let s=slide('真实输出已经有诗句外形，含义仍需检查','扩充五言语料 · 从随机参数训练 · 单条采样原文',results);text(s,'春梦满江南，\n秋风吹赤城。\n露下高秋水，\n烟霞湿牛歌。',115,216,470,320,47,C.ink);text(s,'我们能观察什么',690,198,480,50,32,C.blue,true);text(s,'四句，每句五字\n标点与分行已出现\n“烟霞湿牛歌”搭配不自然',690,272,500,190,31);text(s,'开头“春” · 种子2026\n温度0.8 · 第3000步权重',690,500,490,90,25,C.gray);note(s,'课堂目标：实现正确、流程可复现，并能分析生成结果的局限。');}
// 04
{let s=slide('一整段生成，可以拆成下一字符预测','公式中的竖线表示“给定前缀”；每次输出词表上的条件概率。');formula(s,'pθ(x₂,…,xₜ₊₁ | x₁) = ∏ᵢ₌₁ᵀ pθ(xᵢ₊₁ | x≤ᵢ)',72,169,1130,34);math(s,'prefix_definitions',72,292,1130,23,null,'left',40);cells(s,'春梦满',80,330);let m=box(s,'同一个模型',400,330,210,72);let n=box(s,'江',750,330,72,72,C.warm);link(s,m,n);text(s,'前缀',80,425,200,45,25,C.gray);text(s,'预测并追加',670,425,300,45,25,C.gray);text(s,'下一轮输入：春 梦 满 江',80,515,1060,55,34,C.cyan,true);note(s,'代码对应：T1的右移标签 + T6的循环。“江”为一次采样示意，各次输出由模型概率与采样决定。');}
// 05
{let s=slide('字符编号先变成带位置的表示','T5 · token_emb、pos_emb；一个词元就是一个字符，标点与换行也有编号。');let a=mathBox(s,'字符编号','shape_bt',80,250,240,120),b=mathBox(s,'字符嵌入','shape_btd',430,225,270,110),c=mathBox(s,'位置嵌入','shape_1td',430,390,270,110,C.warm),d=mathBox(s,'逐元素相加','shape_btd',860,300,300,120);link(s,a,b);link(s,b,d);link(s,c,d);text(s,'位置参数按批量轴广播',760,470,430,50,26,C.gray);math(s,'embedding_defaults',65,553,1100,28);note(s,'B：批量数；T：上下文长度；d：表示宽度。上述为本次实验的默认设置。');}
// 06
{let s=slide('因果掩码限定每个位置能读取的前缀','行是查询位置，列是被读取的位置；当前输入位置本身可见。');let chars=['春','梦','满','江','南'];for(let i=0;i<5;i++){text(s,chars[i],95+i*78,179,70,45,28);text(s,chars[i],42,240+i*65,45,45,28);for(let j=0;j<5;j++)box(s,j<=i?'可见':'屏蔽',90+j*78,232+i*65,70,57,j<=i?C.pale:'#E3E6EB',24);}text(s,'“满”这一行',635,220,520,55,34,C.blue,true);text(s,'可读：春、梦、满\n目标：预测“江”\n不可读：江、南',635,300,520,170,32);note(s,'训练时若读到未来字符，验证损失可能虚假变好；自检会改变未来输入并核对前缀输出。');}
// 07
{let s=slide('TinyGPT 把同一条序列送过两个解码器块','只有因果自注意力，没有读取另一段编码器输出的交叉注意力。');let names=['字符 + 位置','解码器块 1','解码器块 2','最终归一化','词表投影'];let objs=names.map((n,i)=>box(s,n,60+i*238,270,207,100,i===4?C.warm:C.pale,27));for(let i=0;i<4;i++)link(s,objs[i],objs[i+1]);math(s,'shape_btd',320,405,500,31);math(s,'shape_btv',1010,405,220,31);text(s,'T4：每个块内部两条残差\nT5：连接嵌入、块和输出层',90,500,1070,90,30);note(s,'V为词表大小。输出是每个位置的原始得分，尚未转换成字符或概率。');}
// 08
{let s=slide('整首划分在前，训练窗口在后','THU-CCPC（THU Chinese Classical Poetry Corpus）五言子集，固定版本0a53d6a2。','来源：code/data/manifest.json、README.md、SOURCE-TERMS.txt；https://github.com/THUNLP-AIPoet/Datasets/tree/master/CCPC。官方划分筛选后非8:1:1；未按作者隔离，近重复未彻底清除。');table(s,[['划分','诗数','字符数','未知字符'],['训练','19,537','566,575','0'],['验证','3,935','114,117','188'],['测试','4,911','142,421','210']],65,200,1150,298,[265,260,330,295],29);text(s,'词表只从训练集建立：5,409项（含未知词元）',65,530,1130,55,31,C.blue,true);note(s,'保持官方归属并核查完全重复；窗口不跨集合。数据仅供学术使用，来源说明随学生包保留。');}
// 09
{let s=slide('默认模型约179万参数，适合观察完整训练流程','2层 · 4个头 · 宽度128 · 上下文32 · 输入与输出嵌入不共享权重',results+' 参数数目由parameter_audit.json和实际模型参数统计核对。');table(s,[['训练设置','数值'],['批量 / 更新次数','64 / 3,000'],['学习率 / 权重衰减','0.0003 / 0'],['丢弃比例 / 随机种子','0.1 / 2026'],['每隔多少步验证','300']],60,205,650,335,[330,320],26);text(s,'1,785,600',775,230,460,90,58,C.blue,true);text(s,'可训练参数',780,340,380,60,31);text(s,'参数量同时受词表大小、\n层数和表示宽度影响',780,440,420,110,27,C.gray);note(s,'完整训练通过107平台Slurm提交；课件使用pro5k预跑记录，107耗时记录在作业日志中。');}
// 10
{let s=slide('六个任务分别落实到一个核心计算','学生主要修改 code/student.py；参数注册、数据读取和训练框架已提供。');table(s,[['任务','公式或计算','代码入口'],['T1','标签右移一位','make_xy'],['T2','拆头与合头','split_heads / merge_heads'],['T3','因果注意力','causal_attention'],['T4','两次残差相加','Block.forward'],['T5','前向与平均交叉熵','TinyGPT.forward / language_loss'],['T6','预测、采样、追加','generate']],60,180,1160,420,[155,425,580],25);s.speakerNotes.text+='\n核心任务由基础张量运算和线性层实现，现成MultiheadAttention、Transformer整层和融合注意力接口不在可用范围内。';}
// 11
{let s=slide('T1：同一片段产生输入和右移标签','教学示例：用6个已知字符构造长度5的训练样本。');text(s,'输入',65,215,130,50,30,C.blue,true);cells(s,'春梦满江南',195,210,62);text(s,'标签',65,330,130,50,30,C.cyan,true);cells(s,'梦满江南，',195,325,62);code(s,'# TODO T1\nx = ...\ny = ...',760,236,430,130,30);math(s,'shifted_targets',80,465,650,34,'2.2.1');note(s,'自检：python checks.py data。若输入和标签完全相同，模型会学复制当前字符。');}
// 12
{let s=slide('T2：拆头改变轴顺序，合头必须做逆操作','');math(s,'head_settings',58,102,1164,26,null,'left',64);let a=mathBox(s,'','shape_25128',70,210,300,80),b=mathBox(s,'','shape_25432',70,355,300,80),c=mathBox(s,'','shape_24532',70,500,300,80,C.warm);link(s,a,b,'bottom','top');link(s,b,c,'bottom','top');text(s,'reshape',405,292,200,45,25,C.gray);text(s,'transpose(1, 2)',405,435,240,45,25,C.gray);code(s,'# split_heads\n# TODO: reshape, transpose\nx = ...\n\n# merge_heads\n# TODO: transpose, reshape\nx = ...',690,205,500,365,25);note(s,'自检：python checks.py heads。合头时先交换“头轴”与“位置轴”，再用reshape合并通道。');}
// 13
{let s=slide('T3：四步实现缩放点积因果注意力','');math(s,'attention_intro',58,108,1164,24,null,'left',55);formula(s,'S = QKᵀ / √k',65,200);formula(s,'P = Softmax(S + M)',65,310);formula(s,'O = PV',65,407);math(s,'attention_dimensions',65,476,570,24,null,'left',40);math(s,'attention_mask',65,523,570,24,null,'left',80);code(s,'# TODO T3: scores + scaling\nscores = ...\n# TODO: causal mask\nallowed = ...\nscores = ...\n# TODO: softmax + value sum\nweights = ...\noutput = ...',675,205,530,350,24);note(s,'对应 causal_attention。mask是全True的[T,T]布尔矩阵；缩放分母使用每头宽度。');}
// 14
{let s=slide('T3手算：第2个位置只能读前两个值','教学设定：缩放后的分数为(1,2,3)，值的一个坐标为(2,6,10)。');formula(s,'(1,2,3)  遮挡后  (1,2,−∞)',65,195,1130,34);chart(s,'bar',['位置1','位置2','位置3'],[{name:'注意力权重',values:[.268941,.731059,0],fill:C.blue}],65,315,520,260,{hasLegend:false,yAxis:{min:0,max:1,numberFormatCode:'0.0',textStyle:{fontSize:22}},dataLabels:{showValue:true,numberFormatCode:'0.000',textStyle:{fontSize:22}}});text(s,'加权结果',685,315,480,50,32,C.blue,true);math(s,'weighted_example',685,390,510,34,null,'left',165);note(s,'先掩码再Softmax；如果先归一化再清零，注意力权重和就可能不再为1。');}
// 15
{let s=slide('T4：前置归一化之后，依次完成两条残差','LN（Layer Normalization，层归一化）按每个位置的通道统计。');let x=box(s,'层输入',70,200,130,65),n=box(s,'LN → Attention',275,200,325,65),u=mathBox(s,'','residual_first',280,345,320,70,C.warm),f=box(s,'LN → FFN',280,485,320,65),o=mathBox(s,'','residual_second',70,570,320,60,C.warm);link(s,x,n);link(s,n,u,'bottom','top');link(s,x,u,'bottom','left');link(s,u,f,'bottom','top');link(s,f,o,'bottom','right');link(s,u,o,'left','top',C.cyan);code(s,'# TODO T4\n# LN -> Attention -> Add\nx = ...\n# LN -> FFN -> Add\nx = ...',730,245,450,210,27);text(s,'FFN（Feed-Forward Network）\n逐位置使用相同前馈变换',730,500,480,75,25);math(s,'ffn_widths',730,572,480,27);s.speakerNotes.text+='\nU为第一条残差结果，第二个子层读取U。蓝色分支表示第一条残差，青色分支表示第二条残差。层号在图中省略，正式公式见讲义4.1。';}
// 16
{let s=slide('T5：给真实下一字更高概率，就会得到更小损失','');math(s,'loss_definitions',58,108,1164,24,null,'left',55);formula(s,'ℒB = −(1/BT) ∑ₙ ∑ᵢ log pθ(yᵢ⁽ⁿ⁾ | x≤ᵢ⁽ⁿ⁾)',65,190,1140,34);code(s,'logits = model(x)  # [B,T,V]\n# TODO T5: flatten B and T\n# mean cross-entropy\nloss = ...',650,355,550,180,25);text(s,'正确字概率：0.75、0.50',70,344,530,45,28);math(s,'loss_example',70,399,530,28,null,'left',115);math(s,'perplexity_example',70,534,530,28,null,'left',50);note(s,'PPL（Perplexity，困惑度）反映预测不确定性。F.cross_entropy接收原始得分，在内部完成归一化。');}
// 17
{let s=slide('T5：一次更新把预测误差传回全部参数','自动求导负责链式法则，学生要保证前向计算和损失连接正确。');let labels=['清空梯度','前向与损失','反向传播','梯度裁剪','参数更新'];let nodes=labels.map((n,i)=>box(s,n,65+i*235,205,200,75,C.pale,27));for(let i=0;i<4;i++)link(s,nodes[i],nodes[i+1]);code(s,'optimizer.zero_grad()\nloss = language_loss(model(x), y)\nloss.backward()\nclip_grad_norm_(model.parameters(), 1.0)\noptimizer.step()',100,360,1060,205,27);note(s,'自检覆盖：前缀因果性、有限损失、非零梯度和权重确实改变。');}
// 18
{let s=slide('T6：新生成的字符成为下一轮的输入','');math(s,'temperature_intro',58,108,1164,24,null,'left',55);formula(s,'pᵥ(τ) = exp(zᵥ/τ) / ∑ᵣ exp(zᵣ/τ)',65,174,1150,34);math(s,'sampling_definitions',65,294,1150,24,null,'left',45);let a=box(s,'截取最近32字',65,345,260,90),b=box(s,'末位置词表得分',425,345,300,90),c=box(s,'采样并追加',840,345,300,90,C.warm);link(s,a,b);link(s,b,c);text(s,'重复以上过程，直到新增80个字符',65,488,1100,60,34,C.cyan,true);text(s,'温度低：更集中        温度高：更随机        贪心：每次取最大得分',65,570,1140,50,26);note(s,'代码对应 generate：context裁剪、logits[:,−1,:]、multinomial、cat。字符与句式均由模型采样产生。');}
// 19
{let s=slide('107平台：Slurm资源配置','GPU（Graphics Processing Unit，图形处理器）\nCPU（Central Processing Unit，中央处理器）','来源：code/scripts/job.sbatch；用户提供的《坑 of 本科生算力平台.docx》；https://slurm.schedmd.com/sbatch.html。CPU计数按平台配置，可能对应物理核或逻辑线程；1小时是申请上限，实际耗时见作业日志。');
 table(s,[['资源','本实验设置','对应Slurm参数'],['节点 / 任务','1 / 1','--nodes=1；--ntasks=1'],['GPU（每节点）','1张','--gres=gpu:1'],['CPU（每任务）','4个','--cpus-per-task=4'],['主内存（每节点）','8G','--mem=8G'],['最长运行时间','1小时','--time=01:00:00']],65,194,1145,370,[295,220,630],27);
 text(s,'一个训练任务配4个CPU；8G为主内存，显存由分配的GPU决定。',65,580,1140,32,24,C.blue);
 note(s,'分区选本人可用项；QOS（Quality of Service，服务质量）按账号权限选择。');}
// 20
{let s=slide('Web终端：查找自己的环境与工作目录','107网页 → 文件管理 → 进入解压后的code/ → 打开Web终端。','来源：实验06_实验讲义.tex第6.1节；用户提供的《坑 of 本科生算力平台.docx》；https://docs.conda.io/projects/conda/en/stable/commands/env/list.html；https://docs.python.org/3/library/sys.html#sys.executable。这里查询107平台路径。若终端不在code/，先cd到文件管理中显示的code绝对路径。');
 code(s,'pwd\nconda env list',85,205,485,90,28);
 text(s,'pwd：当前目录，填网页的工作目录\n环境列表：选已安装PyTorch的课程环境',615,201,590,110,27);
 text(s,'/your/env/bin/python中的your是占位：整串路径都要替换。',65,341,1145,42,29,C.blue,true);
 text(s,'复制所选环境的完整路径，在末尾加上/bin/python，再验证：',65,397,1145,40,27);
 code(s,'export LAB06_PYTHON="/your/env/bin/python"\n"$LAB06_PYTHON" -c "import sys; print(sys.executable)"\n"$LAB06_PYTHON" -c "import torch; print(torch.__version__)"',85,465,1110,110,25);
 note(s,'以上命令查询107平台路径。每个新建网页作业单独填写解释器路径和环境变量。');}
// 21
{let s=slide('107网页提交：四类作业','工作目录填code/的绝对路径；网页命令已在Slurm作业内，使用run-job.sh。','来源：实验06_实验讲义.tex第6.2节；code/scripts/run-job.sh。网页表单已设置节点、GPU、时限等资源；任务数、CPU和主内存若无表单字段，以命令开头的SBATCH行补充。每项资源在表单或命令中设置一次。');let names=['smoke\n20步检查','train\n3000步训练','sample\n原始续写','evaluate\n最终测试'];let nodes=names.map((n,i)=>box(s,n,65+i*300,200,255,100,i===3?C.warm:C.pale,28));for(let i=0;i<3;i++)link(s,nodes[i],nodes[i+1]);code(s,'#SBATCH --ntasks=1\n#SBATCH --cpus-per-task=4\n#SBATCH --mem=8G\nexport LAB06_PYTHON="/your/env/bin/python"\nexport LAB06_DATA_DIR="$PWD/data"\nbash scripts/run-job.sh smoke',90,365,1080,200,26);note(s,'任务数、CPU与内存若已在表单设置，删去对应SBATCH行。\nsmoke成功后新建train作业；普通Web终端提交使用submit.sh。');}
// 22
{let s=slide('权重、词表、配置与代码快照共同定义一次实验','先按验证集选模型，再做一次最终测试；恢复训练结果时保持这些内容对应。');code(s,'outputs/train-<jobid>/\n  best.pt\n  run.json\n  history.csv\n  source/\n  bigram_validation.json',80,220,520,300,28);text(s,'best.pt：最低验证损失权重\nrun.json：模型、数据指纹与设备\nhistory.csv：训练/验证轨迹\nsource/：本轮执行代码',720,220,480,260,29);text(s,'权重与训练时的词表配套',720,515,480,65,30,C.blue,true);note(s,'短作业用于检查运行流程，完整训练后评价诗歌质量。队列状态与训练耗时记录在作业日志中。');}
// 23
{let s=slide('“像诗”需要分开检查四种证据','保留全部原始输出，分别评价预测、结构、语义与训练文本重合。');table(s,[['维度','检查方式','能说明什么'],['预测','相同目标上的交叉熵/困惑度','真实下一字的概率'],['结构','首段是否四句、每句五字','句式学习是否稳定'],['语义','逐句搭配与全诗主题','人工指出具体问题'],['记忆','与训练集整句/整首精确比对','是否发现直接复现']],60,195,1160,375,[200,500,460],27);note(s,'精确比对用于发现直接复现；近似改写、押韵和平仄另行分析，原创性需综合判断。');}
// 24
{let s=slide('扩充语料：验证损失在3000步仍在下降','本次3000步预算内，第3000步的验证损失最低；训练时长需结合验证曲线判断。',results);chart(s,'line',hist.map(r=>String(r.step)),[{name:'训练监测',values:hist.map(r=>Number(r.train_loss.toFixed(6))),line:{fill:C.blue,width:3}},{name:'完整验证',values:hist.map(r=>Number(r.val_loss.toFixed(6))),line:{fill:C.amber,width:3}}],55,200,770,375,{xAxis:{title:'更新步数',textStyle:{fontSize:22}},yAxis:{title:'交叉熵',textStyle:{fontSize:22}}});text(s,'测试困惑度',880,220,350,55,30,C.gray);text(s,'65.18',880,284,350,90,60,C.blue,true);text(s,'同一测试上的二元基线\n338.35',880,425,350,110,27);note(s,'2层/4头/宽128；固定种子2026。训练监测取前8193字符，验证覆盖全文。设备：pro5k。');}
// 25
{let s=slide('温度改变生成结构的稳定性','相同权重；每种温度5个开头×20份，共100份；统计未修改的首段。',results);chart(s,'bar',['0.6','0.8','1.0','1.2'],[{name:'四句五言比例',values:[55,72,79,78],fill:C.blue}],60,195,760,390,{hasLegend:false,yAxis:{min:0,max:100,title:'比例（%）',textStyle:{fontSize:22}},xAxis:{title:'温度',textStyle:{fontSize:22}},dataLabels:{showValue:true,numberFormatCode:'0"%"',textStyle:{fontSize:25}}});text(s,'72 / 100',880,230,330,85,53,C.blue,true);text(s,'温度0.8的结构合格数\n语义质量另行分析',880,335,330,115,29);text(s,'贪心：0 / 5\n样本少，单独报告',880,500,330,90,26,C.gray);note(s,'这些抽样中未检出整首训练诗复现。0.8、1.0、1.2与贪心是当前学生包的四份生成对照。');}
// 26
{let s=slide('长训练可能提高格式比例，也可能增加背诵','历史小语料对照；同一温度0.8、每组100份。','teacher/pro5k-20261029/long-wd0/last-generation_audit.json；default/generation_audit.json；long-wd1/last-generation_audit.json。grokking背景：https://arxiv.org/abs/2201.02177。实验范围为一种子、两种衰减、10万步；结论对应当前设置。');table(s,[['历史小语料权重','四句五言','整首复现训练诗'],['第1200步，验证最佳','31%','0%'],['无衰减，10万步末尾','70%','51%'],['衰减为1，10万步末尾','46%','0%']],60,195,1160,290,[620,240,300],28);text(s,'输出更像诗，也可能只是记住了训练文本',60,525,1150,55,34,C.red,true);note(s,'本次两组长训练未观察到典型grokking（延迟泛化跃迁）；这一观察对应当前语料、预算与设置。');}
// 27
{let s=slide('两类输出提醒我们：结构和创作能力不能混为一谈','两首均为真实输出，未经修改；左侧为扩充语料，右侧为历史小语料长训练。',results+'右侧来源：long-wd0的10万步贪心输出，完全匹配训练诗。');text(s,'结构合格，语义仍生硬',75,195,540,50,31,C.blue,true);text(s,'春梦满江南，\n秋风吹赤城。\n露下高秋水，\n烟霞湿牛歌。',100,285,490,250,40);text(s,'完整流畅，但命中训练诗',700,195,510,50,31,C.red,true);text(s,'春風等君意，\n亦解欺桃李。\n寫得去時真，\n歸來不相似。',730,285,470,250,40);note(s,'课堂讨论：分别指出一个可观察优点、一个问题，以及还需要补充的证据。');}
// 28
{let s=slide('学生对照先固定模型，再改变采样温度','先完成T1–T6与完整训练，再固定数据和模型，对照不同采样规则。');table(s,[['固定','对照安排','记录'],['同一best.pt和代码快照','温度0.8、1.0、1.2','原始文本与生成设置'],['同一开头与种子','增加一份贪心对照','句数、句长、重复'],['同一检查规则','保留全部采样结果','整句/整首训练命中']],60,205,1160,290,[430,350,380],27);text(s,'选做：只改变层数、上下文或位置编码之一',60,535,1140,55,33,C.blue);note(s,'模型方案用验证集选择；测试集只在方案确定后评价。完整训练与报告可课后完成。');}
// 29
{let s=slide('错误可以沿数据流逐段定位','每完成一个任务就运行对应自检，沿数据流逐段定位问题。');table(s,[['观察到的现象','优先检查','自检阶段'],['模型只复制输入','标签是否右移','data'],['形状对，但数值错','拆头后是否交换轴','heads'],['前缀受未来输入影响','掩码方向与Softmax轴','attention / model'],['块输出结构不符','第二条残差是否读取更新后的x','block'],['模型没有更新','损失、梯度和optimizer.step','model'],['长提示报错或重复严重','上下文截取、eval模式、采样','generate']],60,190,1160,405,[390,540,230],24);}
// 30
{let s=slide('完成标准包含实现、复现和结果分析','135分钟内安排编码、自检与讨论；评分看实现和分析，文学质量用于课堂讨论。');text(s,'提交的证据',65,195,520,50,34,C.blue,true);text(s,'本人代码与T1–T6自检\n选定训练目录和Slurm日志\n四份原始生成文本与设置\n一次测试结果及简短分析',65,275,570,260,31);text(s,'离开课堂前回答',730,195,490,50,34,C.cyan,true);text(s,'为什么训练能并行，生成要逐字？\n为什么掩码保留对角线？\n为什么格式正确仍需查重？',730,280,470,230,30);note(s,'评分：目标推导15 + T1–T4实现35 + T5–T6自检25 + 训练生成15 + 复现分析10 = 100分。');s.speakerNotes.text+='\n课堂时段：0–10导入，10–30 T1，30–50 T2，50–75 T3，75–95 T4，95–115 T5，115–135 T6，共135分钟。';}
// 31
{let s=slide('附录：参数量来自哪些部分','',results);math(s,'parameter_settings',58,108,1164,24,null,'left',55);table(s,[['部件','参数数目'],['字符嵌入 + 词表输出','1,384,704'],['可学习位置','4,096'],['两个解码器块','396,544'],['最终层归一化','256'],['合计','1,785,600']],65,185,1145,360,[740,405],28);formula(s,'2Vd + Td + L(12d² + 13d) + 2d',65,575,1130,34);}
// 32
{let s=slide('附录：交叉熵梯度为什么是“概率减标签”','');math(s,'gradient_definitions',58,108,1164,24,null,'left',55);formula(s,'ℒpos = −log pᵧ = −zᵧ + log ∑ᵣ exp(zᵣ)',65,195,1160,34);formula(s,'∂ℒpos / ∂zᵥ = −1{v=y} + exp(zᵥ)/∑ᵣ exp(zᵣ)',65,335,1160,34);formula(s,'∂ℒpos / ∂zᵥ = pᵥ − 1{v=y}',65,465,1160,34);math(s,'gradient_reminder',60,617,1150,23,null,'left',55);}
// 33
{let s=slide('附录：Web终端提交与恢复生成','在code/目录执行；先按第20页查路径，train-12345也须替换为实际目录。');code(s,'export LAB06_PYTHON="/your/env/bin/python"\nexport LAB06_DATA_DIR="$PWD/data"\nbash scripts/submit.sh smoke\n# after successful smoke:\nbash scripts/submit.sh train\nsqueue -u "$USER"\n# after successful training:\nls -d outputs/train-*\nexport LAB06_RUN="$PWD/outputs/train-12345"\nexport LAB06_PROMPT="春"\nbash scripts/submit.sh sample\nbash scripts/submit.sh evaluate',85,195,1120,395,25);note(s,'网页作业使用run-job.sh直接执行；每个新作业分别填写环境变量。');}
// 34
{let s=slide('附录：散文清洗是一次没有得到提升的对照','约106.6万字清洗为103.6万字；原始/清洗各3个种子，共6轮训练。','来源：teacher/prose-clean-pro5k-20261029/summary.json、protocol.json、manifest.json、清洗对照报告.md。15,017,472参数，10,000步，共930份原始生成。汇总困惑度为平均交叉熵的指数，不是困惑度算术平均。');table(s,[['相同模型、词表与测试集','原始训练','清洗训练'],['平均测试交叉熵','4.569186','4.583423'],['平均交叉熵对应的困惑度','96.47','97.85'],['已知汉字预测准确率','18.12%','17.88%']],65,210,1145,295,[635,255,255],28);text(s,'本次清洗减少了噪声，生成质量仍未改善',65,550,1140,50,34,C.blue,true);note(s,'三个种子的差异小，续写仍有语病和话题漂移；该结果对应本次清洗与训练设置，课堂继续以诗歌为主线。');}
// 35
{let s=slide('资料、代码与实测来源','完整链接、版本和对应文件保存在本页及相关页的教师备注。');text(s,'理论：邱锡鹏《神经网络与深度学习》8.4、13.1\n课程：5.2 Transformer的编码与解码器\n数据：THU-CCPC，版本0a53d6a2，仅供学术使用\n代码：OthersideAI/tinyGPT（minGPT分叉），保留MIT许可\n扩展：Isaac Pérez TinyGPT，纯Python框架实现\n实测：pro5k诗歌、长训练与散文清洗原始记录',65,190,1160,370,30);note(s,'TinyGPT在本课指小型GPT实现；参考项目按各仓库作者标注来源。');s.speakerNotes.text='本地资料：source/pdf/nndl-v2.pdf第246–247、375–376页；source/slides/5.2 Transformer的编码与解码器.pdf；实验06_实验讲义.tex；teacher/pro5k-20261029/实测与数据评估.md；teacher/prose-clean-pro5k-20261029/清洗对照报告.md。\n外部原始资料：https://github.com/THUNLP-AIPoet/Datasets/tree/master/CCPC；https://aclanthology.org/P19-3005/；https://github.com/OthersideAI/tinyGPT/tree/e8564668c00b65af1bb7afac3f4c9d15e725c29f；https://isaacperez.github.io/posts/TinyGPT/；https://arxiv.org/abs/1706.03762；https://aclanthology.org/N19-1423/；https://arxiv.org/abs/2201.02177。图示为本课绘制的可编辑教学图，实测图表根据原始运行记录重建。';}
await fs.mkdir(path.join(BUILD,'render'),{recursive:true});
for(let i=0;i<P.slides.items.length;i++){let s=P.slides.items[i];await fs.writeFile(path.join(BUILD,`render/slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await (await P.export({slide:s,format:'png',scale:1})).arrayBuffer()));}
await fs.writeFile(path.join(BUILD,'titles.json'),JSON.stringify(titles,null,2));
await fs.writeFile(path.join(BUILD,'geometry.json'),JSON.stringify(geometries,null,2));
await fs.writeFile(path.join(BUILD,'formula-audit.json'),JSON.stringify(formulaAudit,null,2));
await (await PresentationFile.exportPptx(P)).save(path.join(BUILD,'candidate.pptx'));
console.log('Exported '+P.slides.items.length+' slides');
await fs.mkdir(path.join(BUILD,'publish'),{recursive:true});
const finalPath=path.join(BUILD,'publish/validated.pptx');
const result=await finalizePresentation({workspaceDir:BUILD,candidatePath:path.join(BUILD,'candidate.pptx'),finalPath,pythonExecutable:process.env.PRESENTATION_PYTHON,integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),explicitTotalSlideCount:35,requiredNativeTableOwnerSlides:[2,8,9,10,19,23,26,28,29,31,34],requiredNativeChartOwnerSlides:[14,24,25],materializeLiteralChartWorkbooks:true,layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit',...([2,8,9,10,19,23,26,28,29,31,34].flatMap(n=>['--require-native-table-slide',String(n)]))],fontPolicy:{basis:'design',families:[FONT,MONO]},verifyArtifactToolImport:true,receiptPath:path.join(BUILD,'validation.json')});
await fs.mkdir(OUT,{recursive:true});
await fs.copyFile(finalPath,path.join(OUT,'实验06_TinyGPT五言诗生成.pptx'));
await fs.copyFile(path.join(BUILD,'render/slide-02.png'),path.join(OUT,'任务对照预览.png'));
await fs.copyFile(path.join(BUILD,'render/slide-13.png'),path.join(OUT,'公式排版预览.png'));
console.log(JSON.stringify({finalPath,validated:!!result}));
