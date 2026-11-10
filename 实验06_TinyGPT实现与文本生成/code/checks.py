"""分阶段自检；运行 python checks.py data / heads / attention / block / model / generate / all。"""
import argparse
import math

import torch
from torch import nn

import student


def check_data(api):
    """检查下一字符标签的实际数值。

    Args:
        api (module): 学生模块或教师参考模块。
    """
    x, y = api.make_xy(torch.tensor([4, 2, 3, 3, 1]))
    assert x.tolist() == [4, 2, 3, 3], "T1: 输入应去掉最后一项"
    assert y.tolist() == [2, 3, 3, 1], "T1: 标签必须向前错一位"
    x, y = api.make_xy(torch.tensor([4, 2]))
    assert x.tolist() == [4] and y.tolist() == [2]


def check_heads(api):
    """用通道编号检查拆头和合头，避免形状正确但内容错位。

    Args:
        api (module): 待检查模块。
    """
    x = torch.arange(48).reshape(2, 3, 8).float()
    heads = api.split_heads(x, 2)
    assert heads.shape == (2, 2, 3, 4), "T2.1: 拆头形状错误"
    torch.testing.assert_close(heads[1, 1, 2], torch.tensor([44., 45., 46., 47.]))
    torch.testing.assert_close(heads[0, 1, 0], torch.tensor([4., 5., 6., 7.]))
    torch.testing.assert_close(api.merge_heads(heads), x)


def check_attention(api):
    """核验缩放、掩码方向、行归一化与值的加权和。

    Args:
        api (module): 待检查模块。
    """
    q = torch.tensor([2., 0., 0., 0.]).repeat(1, 1, 3, 1)
    k = torch.tensor([[1., 0., 0., 0.], [2., 0., 0., 0.], [3., 0., 0., 0.]])
    k = k.reshape(1, 1, 3, 4)
    v = torch.tensor([2., 6., 10.]).reshape(1, 1, 3, 1).expand(1, 1, 3, 4)
    out, weights = api.causal_attention(q, k, v)
    expected = torch.tensor([1 / (1 + math.e), math.e / (1 + math.e), 0.])
    torch.testing.assert_close(weights[0, 0, 1], expected)
    torch.testing.assert_close(weights.sum(-1), torch.ones(1, 1, 3))
    assert torch.count_nonzero(torch.triu(weights, diagonal=1)) == 0
    torch.testing.assert_close(out[0, 0, 1], torch.full((4,), 2 * expected[0] + 6 * expected[1]))
    out1, weight1 = api.causal_attention(q[:, :, :1], k[:, :, :1], v[:, :, :1])
    torch.testing.assert_close(out1, v[:, :, :1])
    torch.testing.assert_close(weight1, torch.ones_like(weight1))


def check_block(api):
    """核验两次前置归一化残差的顺序。

    Args:
        api (module): 待检查模块。
    """
    block = api.Block(8, 2, 0.0).eval()
    # 用固定的线性运算替换子层，只检查学生写出的连接顺序。
    for name, scale, shift in [("ln1", 1, 1), ("attn", 2, 0),
                               ("ln2", 1, 3), ("ffn", 4, 0)]:
        layer = nn.Linear(8, 8)
        with torch.no_grad():
            layer.weight.copy_(torch.eye(8) * scale)
            layer.bias.fill_(shift)
        setattr(block, name, layer)
    x = torch.arange(8).float().reshape(1, 1, 8).repeat(2, 4, 1)
    expected = torch.tensor([22., 37., 52., 67., 82., 97., 112., 127.])
    expected = expected.reshape(1, 1, 8).expand_as(x)
    torch.testing.assert_close(block(x), expected)


def check_model(api):
    """检查完整模型的因果性、损失、梯度与一次参数更新。

    Args:
        api (module): 待检查模块。
    """
    torch.manual_seed(26)
    model = api.TinyGPT(11, block_size=8, width=16, n_head=4, n_layer=2, dropout=0.0)
    ids = torch.tensor([[1, 2, 3, 4, 5], [5, 4, 3, 2, 1]])
    model.eval()
    logits = model(ids)
    assert logits.shape == (2, 5, 11), "T5: 应保留批量与位置轴"
    changed = ids.clone()
    changed[:, 3:] = 8
    torch.testing.assert_close(logits[:, :3], model(changed)[:, :3], atol=1e-6, rtol=1e-5)
    assert not torch.allclose(logits[:, 3:], model(changed)[:, 3:]), "输出不能与输入无关"
    scores = torch.log(torch.tensor([[[1., 3.], [2., 2.]]]))
    expected = -(math.log(0.75) + math.log(0.5)) / 2
    torch.testing.assert_close(api.language_loss(scores, torch.tensor([[1, 0]])), torch.tensor(expected))
    model.train()
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.0)
    before = model.blocks[0].attn.query.weight.detach().clone()
    loss = api.language_loss(model(ids), (ids + 1) % 11)
    loss.backward()
    for name, parameter in model.named_parameters():
        assert parameter.grad is not None, f"参数没有梯度: {name}"
        assert torch.isfinite(parameter.grad).all(), f"梯度非有限: {name}"
    optimizer.step()
    assert not torch.equal(before, model.blocks[0].attn.query.weight), "查询权重没有更新"


class SpaceModel(nn.Module):
    """总是生成编号1（假设为空格），检查采样不会遇空格退出。"""

    def __init__(self):
        """允许最长两个上下文字符。"""
        super().__init__()
        self.block_size = 2

    def forward(self, ids):
        """返回确定性得分。

        Args:
            ids (Tensor): [B,T]。

        Returns:
            Tensor: [B,T,3]，编号1几乎确定。
        """
        assert 1 <= ids.shape[1] <= self.block_size, "T6: 未裁剪上下文"
        logits = torch.full((*ids.shape, 3), -100.0, device=ids.device)
        logits[:, :, 1] = 100.0
        return logits


def check_generate(api):
    """同时检查贪心和采样、批量与超长提示词。

    Args:
        api (module): 待检查模块。
    """
    prompt = torch.tensor([[2, 0, 2], [0, 2, 0]])
    for greedy in [True, False]:
        result = api.generate(SpaceModel(), prompt, steps=5, temperature=0.8, greedy=greedy)
        assert result.shape == (2, 8), "T6: 必须生成指定数量的字符"
        torch.testing.assert_close(result[:, :3], prompt)
        torch.testing.assert_close(result[:, 3:], torch.ones(2, 5, dtype=torch.long))
    torch.testing.assert_close(api.generate(SpaceModel(), prompt, steps=0), prompt)


CHECKS = {"data": check_data, "heads": check_heads, "attention": check_attention,
          "block": check_block, "model": check_model, "generate": check_generate}


def run_checks(api, stage="all"):
    """执行所选阶段；遇到错误按自然断言定位。

    Args:
        api (module): 待检查模块。
        stage (str): 一个阶段名或 all。
    """
    torch.set_num_threads(2)
    names = list(CHECKS) if stage == "all" else [stage]
    for name in names:
        CHECKS[name](api)
        print(f"{name}: 通过")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=[*CHECKS, "all"], nargs="?", default="all")
    run_checks(student, parser.parse_args().stage)
