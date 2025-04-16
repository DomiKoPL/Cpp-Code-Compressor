import string
import enum
import itertools
import argparse


SPECIAL = "()[]{}<>;,.+-*/\=&^|! \n\t"


class TokenType(enum.Enum):
    STANDARD = 1
    DEFINE = 2
    STRING = 3
    CHAR = 4
    COMMENT = 5
    NUMBER = 6
    SPECIAL = 7


class TokenizerState(enum.Enum):
    NONE = 0
    STANDARD = 1
    DEFINE = 2
    STRING = 3
    CHAR = 4
    COMMENT = 5
    NUMBER = 6


class Token:
    def __init__(self, token: str, token_type: TokenType) -> None:
        self.token = token
        self.type = token_type

    def __repr__(self) -> str:
        return f"Token({repr(self.token)}, {self.type})"

    def __str__(self) -> str:
        return self.token


class Tokenizer:
    def __init__(self, code: str) -> None:
        self.state = TokenizerState.NONE
        self.idx = 0
        self.cur_token = ""
        self.code = code
        self.tokens = []

        self.tokenize()

    def tokenize_none(self) -> None:
        c = self.code[self.idx]

        if c == "#":
            self.state = TokenizerState.DEFINE
            return

        if c == "\"":
            self.state = TokenizerState.STRING
            return

        if c == "'":
            self.state = TokenizerState.CHAR
            return

        # TODO: This only works for one line comment, add state for multi line comment.
        if c == "/" and self.idx + 1 < len(self.code) and self.code[self.idx + 1] == "/":
            self.state = TokenizerState.COMMENT
            return

        if c.isdigit():
            self.state = TokenizerState.NUMBER
            return

        self.state = TokenizerState.STANDARD
        return

    def tokenize_define(self) -> None:
        c = self.code[self.idx]
        self.cur_token += c

        if c == "\n":
            self.tokens.append(Token(self.cur_token, TokenType.DEFINE))
            self.cur_token = ""
            self.state = TokenizerState.NONE

        self.idx += 1

    def tokenize_string(self) -> None:
        c = self.code[self.idx]
        self.cur_token += c

        if len(self.cur_token) > 1 and c == "\"":
            self.tokens.append(Token(self.cur_token, TokenType.STRING))
            self.cur_token = ""
            self.state = TokenizerState.NONE

        self.idx += 1

    def tokenize_char(self) -> None:
        c = self.code[self.idx]
        self.cur_token += c

        if len(self.cur_token) > 1 and c == "'":
            self.tokens.append(Token(self.cur_token, TokenType.CHAR))
            self.cur_token = ""
            self.state = TokenizerState.NONE

        self.idx += 1

    def tokenize_comment(self) -> None:
        c = self.code[self.idx]

        if c == "\n":
            self.cur_token = ""
            self.state = TokenizerState.NONE

        self.idx += 1

    def tokenize_number(self) -> None:
        c = self.code[self.idx]

        if c.isdigit() or c in "xX_'ULL.fFxull" or c.lower() in "abcdef":
            self.cur_token += c
            self.idx += 1
            return

        self.tokens.append(Token(self.cur_token, TokenType.NUMBER))
        self.cur_token = ""
        self.state = TokenizerState.NONE

    def tokenize_standard(self) -> None:
        c = self.code[self.idx]
        self.idx += 1

        if c in SPECIAL:
            self.tokens.append(Token(self.cur_token, TokenType.STANDARD))
            self.tokens.append(Token(c, TokenType.SPECIAL))
            self.cur_token = ""
            self.state = TokenizerState.NONE
            return

        self.cur_token += c

    def tokenize(self) -> list[Token]:
        state_to_fun = {
            TokenizerState.NONE: self.tokenize_none,
            TokenizerState.DEFINE: self.tokenize_define,
            TokenizerState.STRING: self.tokenize_string,
            TokenizerState.CHAR: self.tokenize_char,
            TokenizerState.COMMENT: self.tokenize_comment,
            TokenizerState.NUMBER: self.tokenize_number,
            TokenizerState.STANDARD: self.tokenize_standard,
        }

        while self.idx < len(self.code):
            state_to_fun.get(self.state)()

        return list(filter(lambda token: len(token.token) > 0, self.tokens))


class Compressor():
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens

        for token in tokens:
            print(repr(token))

        print(f"{len(tokens) = }")

    def filter_spaces(self, remove_new_lines: bool) -> None:
        new_tokens = []

        whitespace = " \t"
        if remove_new_lines:
            whitespace += "\n"

        for i in range(len(self.tokens)):
            if self.tokens[i].token in whitespace:
                if i - 1 >= 0 and self.tokens[i - 1].token in SPECIAL:
                    continue
                if i + 1 < len(self.tokens) and self.tokens[i + 1].token in SPECIAL:
                    continue
            new_tokens.append(self.tokens[i])

        self.tokens = new_tokens

    def create_defines(self) -> None:
        def create_blocked_tokens() -> set[str]:
            blocked = set()

            for c in SPECIAL:
                blocked.add(c)

            for token in self.tokens:
                blocked.add(str(token))

            return blocked

        blocked_tokens = create_blocked_tokens()

        cnt = {}
        for token in self.tokens:
            if token.type != TokenType.STANDARD:
                continue
            cnt[token.token] = cnt.get(token.token, 0) + 1

        def gen_token():
            for d in range(1, 100):
                for x in itertools.product(string.ascii_letters, repeat=d):
                    s = "".join(x)
                    if s not in blocked_tokens:
                        yield s

        new_defines = []

        token_generator = gen_token()
        cur_token: Token | None = None
        token_map = {}

        for token, count in sorted(cnt.items(), key=lambda x: -x[1]):
            if count == 1:
                continue

            if cur_token is None:
                cur_token = next(token_generator)

            if len(token) <= len(cur_token):
                continue

            print(f"{token} --- {count}")
            token_map[token] = cur_token
            new_defines.append(f"#define {cur_token} {token}\n")
            cur_token = None

        self.new_defines = new_defines
        self.tokens = list(
            map(lambda x: token_map.get(x.token, x.token), self.tokens))

    def gen_code(self) -> str:
        # I can't define anything before any include.
        # It wouldn't compile for sure!

        tokens = self.tokens

        def find_last_include():
            for idx, token in enumerate(tokens[::-1]):
                if token.startswith("#include"):
                    return len(tokens) - 1 - idx
            return None

        code = []
        idx = find_last_include()
        if idx is not None:
            code.append("".join(tokens[:idx+1]))
            tokens = tokens[idx + 1:]

        code.append("".join(self.new_defines))
        code.append("".join(tokens))
        return "".join(code)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "file", type=str, help="The path to the file with the code to compress.")
    parser.add_argument("out_file", type=str,
                        help="The path for compressed code.")
    parser.add_argument("--remove_new_lines",
                        action=argparse.BooleanOptionalAction)

    args = parser.parse_args()

    # read code
    with open(f"{args.file}", "r") as file:
        code = file.read()

    tokens = Tokenizer(code).tokenize()

    compressor = Compressor(tokens)
    compressor.filter_spaces(args.remove_new_lines)
    compressor.create_defines()

    code = compressor.gen_code()

    # save final code
    with open(f"{args.out_file}", "w") as file:
        file.write(code)


if __name__ == "__main__":
    main()
