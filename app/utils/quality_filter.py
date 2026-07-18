def is_quality_opportunity(item, score):

    name = (
        item.get("name", "")
        .lower()
        .strip()
    )

    description = (
        item.get("description", "")
        .lower()
    )

    source = (
        item.get("source", "")
        .lower()
    )


    # حذف موارد عمومی و بی‌ارزش
    blacklist = [
        "content",
        "api",
        "home",
        "test",
        "example",
        "template",
        "awesome-list",
        "awesome list",
        "view bounty",
        "learn more",
    ]


    for word in blacklist:

        if word in name:
            return False


    # حداقل نام معتبر
    if len(name) < 3:
        return False


    # فرصت‌های امنیتی ارزشمند
    if "immunefi" in source:
        return score >= 50


    # GitHub و منابع عمومی
    if score < 60:
        return False


    # باید یکی از سیگنال‌ها را داشته باشد
    signals = [
        "ai",
        "security",
        "blockchain",
        "web3",
        "cyber",
        "agent",
        "automation",
        "smart contract",
        "vulnerability",
        "bug",
        "cve",
    ]


    text = name + " " + description


    for signal in signals:

        if signal in text:
            return True


    return score >= 70/
