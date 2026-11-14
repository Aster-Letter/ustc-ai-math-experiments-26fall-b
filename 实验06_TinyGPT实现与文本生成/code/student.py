"""学生任务 T1-T6：每个 TODO 附有 Hint。模型与采样改编自 OthersideAI/tinyGPT，见 THIRD_PARTY_LICENSES.txt。"""
import math

import torch
from torch import nn
from torch.nn import functional as F


def make_xy(chunk):
    """把一段连续词元构造成输入和下一字符标签。

    Args:
        chunk (Tensor): [T+1] 的整数编号。

    Returns:
        tuple: 两个 [T] 张量，输入与标签相差一个位置。
    """
    # TODO T1: 生成相差一位的输入和标签。
    # Hint: chunk 有 T+1 个元素；分别去掉最后、最前一个元素。
    x = chunk[:-1]
    y = chunk[1:]
    return x, y


def split_heads(x, n_head):
    """拆分通道并把头轴移到位置轴前面。

    Args:
        x (Tensor): [B,T,d] 的表示。
        n_head (int): 头数 H，d 必须能被 H 整除。

    Returns:
        Tensor: [B,H,T,d/H]。
    """
    batch, length, width = x.shape
    # TODO T2.1: 拆头并交换轴。
    # Hint: 先得到 [B,T,H,k]，再交换第1、2轴；从0开始编号。
    x = x.reshape(batch, length, n_head, width // n_head)
    return x.transpose(1,2)


def merge_heads(x):
    """把各头的输出按原通道顺序拼回。

    Args:
        x (Tensor): [B,H,T,k]。

    Returns:
        Tensor: [B,T,H*k]。
    """
    batch, heads, length, width = x.shape
    # TODO T2.2: 合头，恢复原来的通道次序。
    # Hint: 先交换头轴与位置轴，再 contiguous().reshape(...)。
    return x.transpose(1,2).contiguous().reshape(batch, length, heads * width)


def causal_attention(q, k, v):
    """计算缩放、掩码、归一化和加权求和。

    Args:
        q (Tensor): 查询，[B,H,T,k]。
        k (Tensor): 键，与查询同形状。
        v (Tensor): 值，与查询同形状。

    Returns:
        tuple: 输出 [B,H,T,k] 和注意力权重 [B,H,T,T]。
    """
    # TODO T3: 缩放点积 -> 因果掩码 -> 按行 Softmax -> 值的加权和。
    # Hint: 缩放分母是每头宽度的平方根；torch.tril 保留对角线。
    # 在 Softmax 前用 masked_fill 把未来位置设为负无穷。
    length = q.shape[-2]
    head_width = q.shape[-1]
    scores = (q@ k.transpose(-2, -1)) / math.sqrt(head_width)
    mask = torch.tril(torch.ones(length, length, device = q.device, dtype = torch.bool))
    scores = scores.masked_fill(~mask, float("-inf"))

    weights = F.softmax(scores, dim = -1)
    output = weights @ v

    return output, weights


class CausalSelfAttention(nn.Module):
    """已提供参数注册；学生完成三个头操作函数。"""

    def __init__(self, width, n_head, dropout):
        """注册查询、键、值和输出投影。

        Args:
            width (int): 表示宽度 d。
            n_head (int): 头数 H。
            dropout (float): 输出分支丢弃概率。
        """
        super().__init__()
        self.query = nn.Linear(width, width)
        self.key = nn.Linear(width, width)
        self.value = nn.Linear(width, width)
        self.proj = nn.Linear(width, width)
        self.drop = nn.Dropout(dropout)
        self.n_head = n_head

    def forward(self, x):
        """对每个位置读取可见前缀。

        Args:
            x (Tensor): [B,T,d]。

        Returns:
            Tensor: [B,T,d]。
        """
        q = split_heads(self.query(x), self.n_head)
        k = split_heads(self.key(x), self.n_head)
        v = split_heads(self.value(x), self.n_head)
        context, _ = causal_attention(q, k, v)
        return self.drop(self.proj(merge_heads(context)))


class Block(nn.Module):
    """带前置层归一化的仅解码器块，无交叉注意力。"""

    def __init__(self, width, n_head, dropout):
        """注册两个子层。

        Args:
            width (int): 表示宽度。
            n_head (int): 头数。
            dropout (float): 分支丢弃概率。
        """
        super().__init__()
        self.ln1 = nn.LayerNorm(width)
        self.ln2 = nn.LayerNorm(width)
        self.attn = CausalSelfAttention(width, n_head, dropout)
        self.ffn = nn.Sequential(
            nn.Linear(width, 4 * width), nn.GELU(),
            nn.Linear(4 * width, width), nn.Dropout(dropout),
        )

    def forward(self, x):
        """依次做两次“前置归一化、子层计算、残差相加”。

        Args:
            x (Tensor): [B,T,d]。

        Returns:
            Tensor: [B,T,d]。
        """
        # TODO T4: 连接两个前置归一化子层和两条残差。
        # Hint: 第一次相加后的 x 才是第二个子层的输入；不是两个并行分支。
        x = x + self.attn(self.ln1(x))
        x = x + self.ffn(self.ln2(x))
        return x


class TinyGPT(nn.Module):
    """字符级生成式预训练 Transformer；本实验从随机参数训练。"""

    def __init__(self, vocab_size, block_size=32, width=128, n_head=4, n_layer=2, dropout=0.1):
        """注册嵌入、块、最终归一化和词表输出层。

        Args:
            vocab_size (int): 词表大小 V，包含未知字符编号0。
            block_size (int): 最长上下文 T_max。
            width (int): 表示宽度 d。
            n_head (int): 头数 H。
            n_layer (int): 块数 L。
            dropout (float): 嵌入和残差分支丢弃概率。
        """
        super().__init__()
        self.block_size = block_size
        self.token_emb = nn.Embedding(vocab_size, width)
        self.pos_emb = nn.Parameter(torch.zeros(1, block_size, width))
        self.drop = nn.Dropout(dropout)
        self.blocks = nn.ModuleList()
        for _ in range(n_layer):
            self.blocks.append(Block(width, n_head, dropout))
        self.ln_f = nn.LayerNorm(width)
        self.head = nn.Linear(width, vocab_size, bias=False)
        self.apply(self._init_weights)

    def _init_weights(self, module):
        """采用参考项目的常用小方差初始化。

        Args:
            module (Module): 当前子模块。
        """
        if isinstance(module, (nn.Linear, nn.Embedding)):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if isinstance(module, nn.Linear) and module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.LayerNorm):
            nn.init.ones_(module.weight)
            nn.init.zeros_(module.bias)

    def forward(self, ids):
        """把整数编号变为下一字符的原始得分。

        Args:
            ids (Tensor): [B,T] 整数编号，1 <= T <= block_size。

        Returns:
            Tensor: [B,T,V] 的 logits，尚未做 Softmax。
        """
        # TODO T5.1: 嵌入相加 -> Dropout -> 所有块 -> ln_f -> head。
        # Hint: 位置参数只取当前 T 项；输出保留 B、T 两个轴。
        length = ids.shape[1]
        x = self.token_emb(ids) + self.pos_emb[:, :length, :]
        x = self.drop(x)
        for block in self.blocks:
            x = block(x)
        x = self.ln_f(x)
        logits = self.head(x)
        return logits

def language_loss(logits, targets):
    """计算所有样本、所有位置的平均交叉熵。

    Args:
        logits (Tensor): [B,T,V] 的原始得分。
        targets (Tensor): [B,T] 整数标签。

    Returns:
        Tensor: 标量平均损失。
    """
    # TODO T5.2: 合并 B、T 两个轴，再计算平均交叉熵。
    # Hint: F.cross_entropy 接收原始得分，不要提前 Softmax；标签是整数。
    vocab_size = logits.shape[-1]
    return F.cross_entropy(logits.reshape(-1, vocab_size), targets.reshape(-1))


@torch.no_grad()
def generate(model, ids, steps, temperature=1.0, greedy=False):
    """截取最近上下文，逐次追加一个词元；空格也是普通词元。

    Args:
        model (TinyGPT): 训练后的模型。
        ids (Tensor): [B,T0] 的非空提示词。
        steps (int): 生成字符数。
        temperature (float): 正温度；只影响随机采样的分布。
        greedy (bool): 为真时取最大得分，否则按概率采样。

    Returns:
        Tensor: [B,T0+steps]，包含原提示词。
    """
    # TODO T6: 重复 steps 次，每次读取最后位置并追加一个字符。
    # Hint: 先裁剪 ids[:, -model.block_size:]；保留完整 ids 用于返回。
    # greedy 时 argmax(..., keepdim=True)，否则 Softmax 后 multinomial。
    # 用 torch.cat(..., dim=1) 追加；空格与换行不能触发提前结束。
    model.eval()
    for _ in range(steps):
        context = ids[:, -model.block_size:]

        logits = model(context)
        next_logits = logits[:, -1, :]

        if greedy:
            next_id = next_logits.argmax(dim = -1, keepdim = True)
        else:
            probs = F.softmax(next_logits /  temperature, dim = -1)
            next_id = torch.multinomial(probs, num_samples = 1)
        
        ids = torch.cat([ids, next_id], dim = 1)

    return ids
