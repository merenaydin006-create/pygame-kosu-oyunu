from openai import OpenAI

client = OpenAI(
    api_key="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"
)

print("🤖 Yapay Zeka Sohbet (çıkmak için 'exit')")

while True:
    user_input = input("Sen: ")

    if user_input.lower() == "exit":
        print("Çıkılıyor...")
        break

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Sen Türkçe konuşan yardımsever bir asistansın."},
            {"role": "user", "content": user_input}
        ]
    )

    print("AI:", response.choices[0].message.content)