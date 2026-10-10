"""按阶段执行的小样例自检；运行方式：python checkpoints.py C2。"""
import sys
import math
import pandas as pd
import torch
from torch.utils.data import SequentialSampler, RandomSampler
import support


def check(implementation, checkpoint):
    """检查一个阶段，避免尚未完成的后续任务阻塞当前阶段。

    Args:
        implementation (module): student 或 reference 模块。
        checkpoint (int): 0 到 7。
    """
    s = implementation
    if checkpoint == 0:
        X = torch.tensor([[1., 2.], [1., -1.]])
        w = torch.tensor([[0.], [1.]])
        assert X.shape == (2, 2)
        assert torch.equal(X @ w, torch.tensor([[2.], [-1.]]))
        frame = support.load_split(support.DATA_DIR, "train")
        print("课堂训练表形状：", frame.shape, "缺失标签：", frame.isDefault.isna().sum())
        print("X @ w =", (X @ w).tolist())
    elif checkpoint == 1:
        frame = pd.DataFrame({"isDefault": [1., float("nan"), 0.], "x": [None, 2., 3.]})
        result = s.filter_labels(frame)
        assert result is not None, "先完成 C1 filter_labels"
        assert result.isDefault.tolist() == [1., 0.]
        assert pd.isna(result.x.iloc[0]), "C1 不填充特征"
        assert len(frame) == 3
        assert [s.encode_employment(x) for x in ["< 1 year", "1 year", "3 years", "10+ years"]] == [1., 2., 4., 12.]
        assert math.isnan(s.encode_employment(float("nan")))
    elif checkpoint == 2:
        frame = pd.DataFrame({"x": [1., 3., None], "constant": [5., 5., 5.], "empty": [None]*3}, dtype=float)
        result = s.fit_statistics(frame)
        assert result is not None, "先完成 C2 fit_statistics"
        means, scales = result
        assert means.tolist() == [2., 5., 0.]
        assert abs(scales.x - math.sqrt(2/3)) < 1e-6
        assert scales["constant"] == scales["empty"] == 1
        val = pd.DataFrame({"x": [100., None], "constant": [5., 5.], "empty": [None, None]}, dtype=float)
        changed = s.apply_statistics(val, means, scales)
        assert abs(changed.x.iloc[0] - 98 / math.sqrt(2/3)) < 1e-5, "不能用验证集自己的均值"
        assert changed.x.iloc[1] == 0
        X, y = s.to_tensors(changed, pd.Series([1, 0]))
        assert X.shape == (2, 4) and y.shape == (2, 1)
        assert X.dtype == y.dtype == torch.float32
        assert torch.isfinite(X).all() and (X[:, 0] == 1).all()
    elif checkpoint == 3:
        X = torch.arange(15).reshape(5, 3).float()
        y = torch.arange(5).reshape(5, 1).float()
        dataset = s.LoanDataset(X, y)
        assert len(dataset) == 5
        row, label = dataset[2]
        assert torch.equal(row, X[2]) and torch.equal(label, y[2])
        loader = s.make_loader(dataset, 2, False)
        assert isinstance(loader.sampler, SequentialSampler)
        assert [len(b[1]) for b in loader] == [2, 2, 1]
        assert torch.equal(torch.cat([b[0] for b in loader]), X)
        loader = s.make_loader(dataset, 2, True)
        assert isinstance(loader.sampler, RandomSampler)
        for row_batch, label_batch in loader:
            assert torch.equal(row_batch[:, 0] / 3, label_batch[:, 0])
    elif checkpoint == 4:
        z = torch.tensor([[-2.], [0.], [2.]])
        p = s.sigmoid(z)
        assert p is not None, "先完成 C4 sigmoid"
        assert torch.allclose(p, torch.tensor([[.11920292], [.5], [.88079708]]))
        assert torch.isfinite(s.sigmoid(torch.tensor([-1000., 1000.]))).all()
        model = s.LogisticRegression(3)
        assert model.theta.shape == (3, 1)
        assert any(parameter is model.theta for parameter in model.parameters())
        with torch.no_grad():
            model.theta.copy_(torch.tensor([[1.], [2.], [-1.]]))
        assert torch.equal(model(torch.tensor([[1., 3., 2.]])), torch.tensor([[5.]])), "forward 应返回得分 5，不是概率"
    elif checkpoint == 5:
        z = torch.zeros((2, 1), requires_grad=True)
        loss = s.data_loss(z, torch.tensor([[1.], [0.]]))
        assert loss is not None, "先完成 C5 data_loss"
        assert abs(loss.item() - math.log(2)) < 1e-6
        loss.backward()
        assert torch.allclose(z.grad, torch.tensor([[-.25], [.25]]))
        extreme = s.data_loss(torch.tensor([[1000.], [-1000.]]), torch.tensor([[0.], [1.]]))
        assert torch.isfinite(extreme) and abs(extreme.item()-1000) < 1e-4
        model = s.LogisticRegression(3)
        with torch.no_grad():
            model.theta.copy_(torch.tensor([[10.], [3.], [-4.]]))
        assert model.penalty("l1").item() == 7
        assert model.penalty("l2").item() == 12.5
        assert model.penalty("none").item() == 0
        model.penalty("l2").backward()
        assert torch.equal(model.theta.grad, torch.tensor([[0.], [3.], [-4.]]))
    elif checkpoint == 6:
        X = torch.tensor([[1., 1., 0.], [1., 0., 1.]])
        y = torch.tensor([[1.], [0.]])
        model = s.LogisticRegression(3)
        loader = s.make_loader(s.LoanDataset(X, y), 2, False)
        optimizer = torch.optim.SGD(model.parameters(), lr=.4)
        loss = s.train_epoch(model, loader, optimizer, "none", 0.)
        assert loss is not None, "先完成 C6 train_epoch"
        expected = torch.tensor([[0.], [.1], [-.1]])
        assert torch.allclose(model.theta.detach(), expected, atol=1e-6)
        # 第二次更新检查梯度是否清零，和课堂公式独立核对。
        gradient = X.T @ (torch.sigmoid(X @ expected) - y) / 2
        s.train_epoch(model, loader, optimizer, "none", 0.)
        assert torch.allclose(model.theta.detach(), expected-.4*gradient, atol=1e-6)
    elif checkpoint == 7:
        y = torch.tensor([[1.], [0.], [1.], [0.]])
        p = torch.tensor([[.9], [.8], [.4], [.1]])
        result = s.binary_metrics(y, p)
        assert result is not None, "先完成 C7 binary_metrics"
        assert [result[k] for k in ["tn", "fp", "fn", "tp"]] == [1, 1, 1, 1]
        assert all(result[k] == .5 for k in ["accuracy", "precision", "recall", "f1"])
        assert s.binary_metrics(torch.ones((1,1)), torch.tensor([[.5]]))["tp"] == 1
        assert s.binary_metrics(y, p, 1.0)["precision"] == 0
    print("C" + str(checkpoint) + " PASS")


def check_all(implementation):
    """依次检查全部阶段。

    Args:
        implementation (module): 待验收实现模块。
    """
    for checkpoint in range(8):
        check(implementation, checkpoint)


if __name__ == "__main__":
    import student
    if len(sys.argv) == 1 or sys.argv[1].lower() == "all":
        check_all(student)
    else:
        check(student, int(sys.argv[1].upper().replace("C", "")))
