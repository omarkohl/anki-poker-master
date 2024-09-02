from anki_poker_master.model.hand import Hand


def to_html(hand: Hand) -> str:
    return f"""<div class="hand-history">
<h1>{hand.title}</h1>
</div>
"""
