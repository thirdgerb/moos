from __future__ import annotations

from typing import List, Iterator, TYPE_CHECKING, Type
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field

if TYPE_CHECKING:  # 同目录的引用全部都用 type checking. python 这一点比 golang 麻烦, 更容易形成循环引用.
    from .kernel import Kernel
    from .messages import Message
    from .thought import Event
    from .context import Context

INSTRUCTION = """
ghost 应该是系统使用者看到的对象. 
而不是 AI 自己看到的自己. 这两者要有所区别. 

给开发者看到的 Interface 要足够简单, 因为我们开发者都是非常非常的 stupid, 不想动一点脑子. 

要考虑同步异步之类的各种问题. 
"""


class Ghost(ABC):
    """
    机器人的灵魂.
    Ghost 本身只有同步接口.
    全异步的调度放在外层, 要克制.
    可以允许外部将 Ghost 包装成 Prototype.
    Prototype 动态去构建 Ghost 的各种组件.
    """

    @abstractmethod
    def kernel(self) -> Kernel:
        pass

    @abstractmethod
    def answer(self, question: str) -> str:
        """
        测试时用的简单接口. 没有什么意义的.
        """
        pass

    @abstractmethod
    def on_message(self, ctx: "Context", message: Message) -> Iterator[Message]:
        """
        假设 Ghost 接受到了一个格式化的消息.
        消息会转化为一个 event, 继续触发.
        """
        pass

    @abstractmethod
    def on_event(self, ctx: "Context",  event: "Event") -> Iterator[Message]:
        """
        on_event 是系统的底层.
        """
        pass


# ---- 会话管理.


# ---- bot 的思维空间.

class Mindset(ABC):
    """
    Ghost 的思维空间.
    合并了 Mindset / Knowledge / Memory
    三者理论上可以互相调用, 只要逻辑上不成环.
    为了让 Ghost 有学习成长的能力.
    """

    @property
    @abstractmethod
    def knowledge_base(self) -> KnowledgeBase:
        pass

    @property
    @abstractmethod
    def memory(self) -> Memory:
        pass


# knowledge

class KnowledgeIndex(BaseModel):
    id: str
    tags: List[str]


class Knowledge(ABC, BaseModel):
    """
    知识的原型结构.
    用 pydantic base model 的形式存储, 因此有它的 schema.
    数据结构就用 dict 了.
    而 type 就是 Knowledge 的类名好了.
    """

    @abstractmethod
    def id(self) -> str:
        """
        每个 knowledge 都需要有一个唯一的 id, 用来做存储和读取的主键.
        """
        pass

    @abstractmethod
    def desc(self) -> str:
        """
        对知识的基础描述,
        """
        pass

    # @abstractmethod
    # def tags(self) -> Dict[str, str]:
    #     """
    #     知识存储时用的索引 tag
    #     tag name => tag description
    #     用来描述 tag indexes 的 key
    #     """
    #     pass
    #
    # @abstractmethod
    # def tag_indexes(self) -> Dict[str, str]:
    #     """
    #     knowledge 的索引使用这种结构:
    #     tag => nature language value
    #     存储时根据 tag 生成相应的 rag index
    #     搜索时, 根据 tag 做多路搜索?
    #     感觉没想明白.
    #     """
    #     pass


class KnowledgeDriver(ABC):

    @abstractmethod
    def match(self, typ: Type[Knowledge]) -> bool:
        pass

    @abstractmethod
    def search(self, desc: str, limit: int, offset: int = 0) -> Iterator[Knowledge]:
        pass

    @abstractmethod
    def retrieve(self, knowledge_id: str) -> Knowledge:
        pass

    @abstractmethod
    def save(self, knowledge: Knowledge) -> None:
        pass


class KnowledgeBase(ABC):
    """
    Ghost 的知识. 要有一种允许开发者给 Ghost 提供知识的方式.

    # dev logs:

    - 如何给知识定义一个超级通用的抽象, 真是难啊.
    - 先简单设计一下
    """

    @abstractmethod
    def register(self, driver: KnowledgeDriver):
        """
        注册一个知识驱动器.
        """
        pass

    @abstractmethod
    def drivers(self) -> Iterator[KnowledgeDriver]:
        pass

    @abstractmethod
    def retrieve(self, typ: Type[Knowledge], knowledge_id: str) -> Knowledge | None:
        pass

    @abstractmethod
    def save(self, knowledge: Knowledge) -> None:
        pass

    @abstractmethod
    def search(
            self,
            typ: Type[Knowledge],
            desc: str,
            limit: int = 5,
            condition: str | None = None,
            offset: int = 0,
    ) -> Iterator[Knowledge]:
        """
        搜索的基本原理:
        1. 条件粗筛
        2. 精筛

        """
        pass


# ---- bot 的 memory

class Memory(ABC):
    """
    记忆空间. 与知识空间的区别是什么?
    记忆假设和 Ghost 自身行为是相关的, 而且是 Ghost 主动驱动的.
    要设计足够通用的 interface.
    """
    pass
