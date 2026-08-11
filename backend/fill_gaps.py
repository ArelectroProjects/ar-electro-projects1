"""Fill missing price hints and photos. Photos reuse the client's own catalogue imagery
(thematically matched); admin can replace any of them from the dashboard."""
import os, asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

W = "https://static.wixstatic.com/media/"
def img(code, ext="jpg"):
    return f"{W}{code}~mv2.{ext}"

FILLS = [
    ("diploma-project", "Smart Energy Meter", "₹2,999 onwards", img("d89d85_64b5d1f0487c46988a23d10556aa6b1d")),
    ("diploma-project", "Automatic Street Light Controller", "₹1,999 onwards", img("d89d85_9a80dba93ecf4dcbba9bf909d775a871", "jpeg")),
    ("diploma-project", "Wireless Notice Board", "₹1,999 onwards", img("d89d85_25fc131f477d469ea56a121bc7fabb17")),
    ("diploma-project", "Industrial Temperature Control", "₹2,499 onwards", img("d89d85_369435b5f6c64fe791c8e2f395af2951")),
    ("diploma-project", "Elevator Overload Alert", "₹2,999 onwards", ""),
    ("diploma-project", "GSM Home Automation", "₹2,499 onwards", img("d89d85_ab478a0b93554756b1cb5686d66155ba")),
    ("degree-project", "Solar MPPT Charge Controller", "₹5,499 onwards", img("d89d85_91ee1c6f337e411e905489926789a1c5")),
    ("degree-project", "EV Battery Management System", "₹6,999 onwards", img("d89d85_968e225f2ecc42c0a1dd2fd2e5b03496")),
    ("degree-project", "Induction Motor Fault Detection", "₹5,999 onwards", img("d89d85_1b37691722974b23a796cd8be31f0ce3")),
    ("degree-project", "Android Motor Speed Control", "₹4,999 onwards", img("d89d85_49b102fabb3f48d6be73e3de24bc49e4", "png")),
    ("degree-project", "Highway Speed Violation Detection", "₹5,499 onwards", img("d89d85_527bd1e7780b4df38bb8d9b0e4d554bc")),
    ("degree-project", "PV Panel Monitoring", "₹4,999 onwards", img("d89d85_70c3b8685bd246b8b660130d7e17ef6c")),
    ("degree-project", "Solar Home Inverter Design", "₹5,999 onwards", img("d89d85_91ee1c6f337e411e905489926789a1c5")),
    ("drone-project", "Quadcopter with Live Camera", "₹9,999 onwards", img("d89d85_3296f027a0854ad1a9c5789276e1d84a")),
    ("drone-project", "Payload Delivery Drone", "₹12,499 onwards", img("d89d85_810810afe9214d1eb89b4bf5018682fa")),
    ("electronics-project", "GSM Gas Leak Detector", "₹2,499 onwards", img("d89d85_2349e716ca5644e0ad10445b007bd64a")),
    ("electronics-project", "RLC Meter", "₹2,999 onwards", img("d89d85_884ca1ad9a8e4ac2ba77efd867a8d709")),
    ("electronics-project", "Power Factor Meter", "₹3,499 onwards", img("d89d85_8bccaa9ff218437f8f28672169005965")),
    ("electronics-project", "Fingerprint Lock for Motors", "₹3,999 onwards", img("d89d85_0e2201981ef54def97fb8b696fe4cd9d")),
    ("electronics-project", "Air Quality Monitoring", "₹2,999 onwards", img("d89d85_88367648dab440e68627c1d1c073f815")),
    ("electrical-project", "Automatic Power Factor Correction", "₹4,999 onwards", img("d89d85_8bccaa9ff218437f8f28672169005965")),
    ("electrical-project", "Underground Cable Fault Detection", "₹4,499 onwards", ""),
    ("electrical-project", "Induction Motor Protection", "₹4,999 onwards", img("d89d85_1b37691722974b23a796cd8be31f0ce3")),
    ("electrical-project", "Star Delta Starter with Display", "₹3,999 onwards", img("d89d85_2638eead5fe444bc9a74f7ff35889d95")),
    ("embedded-project", "Sign Language to Speech Glove", "₹5,999 onwards", ""),
    ("embedded-project", "Solar Panel Tracking", "₹3,499 onwards", img("d89d85_c7a1d355d1fe44b7b3c260e1be752fa4")),
    ("embedded-project", "Gesture Control Car", "₹3,999 onwards", img("d89d85_2cc4baa06083448f84fa0acf239b9dc8")),
    ("embedded-project", "Line Following Robot", "₹2,999 onwards", img("d89d85_2cc4baa06083448f84fa0acf239b9dc8")),
    ("embedded-project", "Colour Sorter Machine", "₹4,499 onwards", ""),
    ("embedded-project", "IR Contactless Tachometer", "₹2,499 onwards", img("d89d85_49b102fabb3f48d6be73e3de24bc49e4", "png")),
    ("embedded-project", "Voice Controlled Wheelchair", "₹5,499 onwards", ""),
    ("mechanical-project", "Pneumatic Sheet Metal Cutter", "₹7,499 onwards", ""),
    ("mechanical-project", "360° Fire Exhausting System", "₹6,999 onwards", img("d89d85_4e38c723deaa4c6ba133176121a06a21")),
    ("mechanical-project", "Agriculture Robot", "₹8,999 onwards", img("d89d85_df8308ef205841b29fe34a375ab7b078", "jpeg")),
    ("mechanical-project", "Laser Engraving Machine", "₹7,999 onwards", ""),
    ("mechanical-project", "Automatic Bottle Filling Machine", "₹6,499 onwards", img("d89d85_f3d7d8fbb1d9423bb95662bfc1973a1b")),
    ("biomedical-project", "Patient Health Monitoring System", "₹4,499 onwards", img("d89d85_91e200760edd4998a72d51ba8b97ed52")),
    ("biomedical-project", "Smart Blind Stick", "₹3,499 onwards", img("d89d85_ae23ec2eb441429c96ce41e0adb793be")),
    ("biomedical-project", "IoT Health Monitoring Kit", "₹4,999 onwards", img("d89d85_91e200760edd4998a72d51ba8b97ed52")),
    ("iot-projects", "Smart Home Automation", "₹3,999 onwards", img("d89d85_ab478a0b93554756b1cb5686d66155ba")),
]

async def main():
    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = client[os.environ["DB_NAME"]]
    priced, imaged, missing = 0, 0, 0
    for category, title, price, image in FILLS:
        doc = await db.projects.find_one({"category": category, "title": {"$regex": f"^{title}$", "$options": "i"}})
        if not doc:
            missing += 1
            print("NOT FOUND:", category, title)
            continue
        updates = {}
        if not doc.get("price_hint") and price:
            updates["price_hint"] = price
        if not doc.get("image") and image:
            updates["image"] = image
        if updates:
            await db.projects.update_one({"id": doc["id"]}, {"$set": updates})
            if "price_hint" in updates: priced += 1
            if "image" in updates: imaged += 1
    no_price = await db.projects.count_documents({"price_hint": ""})
    no_image = await db.projects.count_documents({"image": ""})
    print(f"priced={priced} imaged={imaged} not_found={missing} still_no_price={no_price} still_no_image={no_image}")
    client.close()

asyncio.run(main())
