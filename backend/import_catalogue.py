"""One-time bulk import of the AR Electro Projects catalogue (recovered from arelectroprojects.com archive).
Safe to re-run: skips titles that already exist in the same category."""
import os, uuid, asyncio
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

W = "https://static.wixstatic.com/media/"
def img(code, ext="jpg"):
    return f"{W}{code}~mv2.{ext}"

CATALOGUE = [
    # IoT Projects
    ("iot-projects", "Gas Leakage Detection", "IoT based gas leakage detection with Blynk 2.0 app alerts.", img("d89d85_83fefd417147473fab6e44c01745ff50")),
    ("iot-projects", "Air Purifier", "IoT based air purifier with Google Assistant control.", img("d89d85_88367648dab440e68627c1d1c073f815")),
    ("iot-projects", "BLDC Motor Speed Control", "IoT based BLDC motor speed control with RPM monitoring.", img("d89d85_49b102fabb3f48d6be73e3de24bc49e4", "png")),
    ("iot-projects", "Forest Fire Detection", "IoT based forest fire detection system with instant alerts.", img("d89d85_4e38c723deaa4c6ba133176121a06a21")),
    ("iot-projects", "Green House Monitoring & Control", "IoT based green house monitoring and control system.", img("d89d85_3af8fe9c252845a8a9b2868d913bf910")),
    ("iot-projects", "IoT Based Refrigerator", "Refrigerator control and monitoring over the internet.", img("d89d85_50e6f1ccaa5d4c94b54c866362b345e0")),
    ("iot-projects", "IoT Weather Monitoring", "Weather monitoring on LCD with Blynk 2.0 dashboard.", img("d89d85_25fc131f477d469ea56a121bc7fabb17")),
    ("iot-projects", "IoT AC Load Monitoring", "AC load monitoring with timer and Blynk 2.0.", img("d89d85_14cbfb2c46264c8ca06f3d803a26674f")),
    ("iot-projects", "Patient Health Monitoring System", "IoT based patient health monitoring system.", img("d89d85_91e200760edd4998a72d51ba8b97ed52")),
    ("iot-projects", "Transformer Monitoring & Protection", "IoT based transformer monitoring and protection system.", img("d89d85_6bcd6a27cf0a441db33f58992d425b3c")),
    ("iot-projects", "Substation Monitoring & Protection", "IoT based substation monitoring and protection.", img("d89d85_04f52c3a96e445058ea32e9f40d3055f")),
    ("iot-projects", "Wireless Power Transmission", "Wireless power transfer demonstration system.", img("d89d85_2a8d1772c3644c90b66a742a8f4de0af")),
    ("iot-projects", "Biometric Door Lock with Mobile App", "Fingerprint door lock controlled from a mobile app.", img("d89d85_0e2201981ef54def97fb8b696fe4cd9d")),
    # Electrical Projects
    ("electrical-project", "EV Wireless Charging using Solar", "Solar based wireless EV charging system.", img("d89d85_968e225f2ecc42c0a1dd2fd2e5b03496")),
    ("electrical-project", "Automatic Traffic Light", "Automatic traffic light with speed breaker control.", img("d89d85_527bd1e7780b4df38bb8d9b0e4d554bc")),
    ("electrical-project", "DC Motor Protection System", "GSM based DC motor protection system.", img("d89d85_1b37691722974b23a796cd8be31f0ce3")),
    ("electrical-project", "Energy Generation from Speed Breaker", "Kinetic energy harvest from road speed breakers.", img("d89d85_77ac9c88ac9142bfb5a7c0f5a0681330", "png")),
    ("electrical-project", "Induction Heating", "Induction heating system with 200W capacity.", img("d89d85_df88215d78e84aca819c6b32fd2fd9ea")),
    ("electrical-project", "Password Based Circuit Breaker", "Arduino based circuit breaker with password control.", img("d89d85_7bb91964afdf45579058ec888db14bb8")),
    ("electrical-project", "Prepaid Energy Meter with Theft Detection", "Prepaid metering with power-theft detection.", img("d89d85_64b5d1f0487c46988a23d10556aa6b1d")),
    ("electrical-project", "Automatic Transformer Load Sharing", "Automatic load sharing between transformers.", img("d89d85_5be5cf38eea74500b3b831a9be365a38")),
    ("electrical-project", "Transformer Health Monitoring", "Health monitoring with protection system.", img("d89d85_3f9f9bbaeb614b91b6947b8f39f8b662")),
    ("electrical-project", "Solar EV Charging on Road", "Wireless EV charging while the vehicle is in motion.", img("d89d85_726faa3956e44ab78cb89e8c10b1ebd7")),
    ("electrical-project", "Hybrid Power System", "Dual power generation from solar and wind mill.", img("d89d85_7b84dd000fd44bd6b4e8cba62bf4c517")),
    ("electrical-project", "Solar Panel Cleaning System", "Automatic solar panel cleaning control system.", img("d89d85_70c3b8685bd246b8b660130d7e17ef6c")),
    ("electrical-project", "Solar Street Light System", "Automatic solar based street light system.", img("d89d85_9a80dba93ecf4dcbba9bf909d775a871", "jpeg")),
    ("electrical-project", "Dual Axis Solar Tracking", "Dual axis solar tracking system using Arduino.", img("d89d85_c7a1d355d1fe44b7b3c260e1be752fa4")),
    ("electrical-project", "Solar Water Irrigation System", "Automatic solar powered water irrigation system.", img("d89d85_df8308ef205841b29fe34a375ab7b078", "jpeg")),
    ("electrical-project", "Single Axis Solar Tracker", "Single axis solar tracker system.", img("d89d85_91dcc552f4b64b0b93f073c98e2bc60e")),
    ("electrical-project", "Solar-Powered Inverter", "Arduino based inverter using MOSFET.", img("d89d85_91ee1c6f337e411e905489926789a1c5")),
    ("electrical-project", "Underground Cable Fault Detection", "Locates faults in underground cables precisely.", ""),
    ("electrical-project", "Induction Motor Protection", "1-phase or 3-phase induction motor protection system.", ""),
    ("electrical-project", "Star Delta Starter with Display", "Star delta starter with display and adjustable delay timer.", ""),
    # Electronics Projects
    ("electronics-project", "Alcohol Detection with Engine Lock", "Alcohol detection system with engine lock.", img("d89d85_abbe1cb687484eec938bcfb206f31fe4", "png")),
    ("electronics-project", "LPG Gas Leakage Detection", "GSM based LPG gas leakage detection.", img("d89d85_67695e0aceb247febdd3d24866a523ef")),
    ("electronics-project", "Humidity & Temperature Controller", "Incubator humidity and temperature controller.", img("d89d85_369435b5f6c64fe791c8e2f395af2951")),
    ("electronics-project", "Smoke Detector", "Standalone smoke detection and alarm system.", img("d89d85_e394b3660f1a4fe4b1eeb685d6600167")),
    ("electronics-project", "Microcontroller Based SMPS", "Switched-mode power supply with microcontroller control.", img("d89d85_884ca1ad9a8e4ac2ba77efd867a8d709")),
    ("electronics-project", "Gas Leakage Detector with Call Alert", "Gas detector that triggers an automatic call alert.", img("d89d85_2349e716ca5644e0ad10445b007bd64a")),
    ("electronics-project", "RLC Meter", "Precision resistance, inductance and capacitance meter.", ""),
    ("electronics-project", "Power Factor Meter", "Microcontroller based power factor measurement.", ""),
    ("electronics-project", "Fingerprint Lock for Motors", "Fingerprint lock for AC and DC motor control.", ""),
    ("electronics-project", "Air Quality Monitoring", "Real-time air quality measurement and display.", ""),
    # Embedded Projects
    ("embedded-project", "Automatic Power Factor Correction", "Capacitor bank switching with microcontroller control.", img("d89d85_8bccaa9ff218437f8f28672169005965")),
    ("embedded-project", "GSM DC Motor Speed Control", "GSM based DC motor speed control system.", img("d89d85_2638eead5fe444bc9a74f7ff35889d95")),
    ("embedded-project", "Wireless Water Level Indicator", "IoT based wireless water level indicator.", img("d89d85_f3d7d8fbb1d9423bb95662bfc1973a1b")),
    ("embedded-project", "Home Automation (ATMEGA328)", "Home automation using ATMEGA328 microcontroller.", img("d89d85_ab478a0b93554756b1cb5686d66155ba")),
    ("embedded-project", "Solar Panel Tracking", "Solar panel sun tracking with Atmega328.", ""),
    ("embedded-project", "Gesture Control Car", "Hand-gesture controlled robotic car.", ""),
    ("embedded-project", "Line Following Robot", "Autonomous line following robot.", ""),
    ("embedded-project", "Colour Sorter Machine", "Automatic colour based sorting machine.", ""),
    ("embedded-project", "IR Contactless Tachometer", "IR sensor based contactless RPM measurement.", ""),
    ("embedded-project", "Voice Controlled Wheelchair", "Voice control car / wheelchair platform.", ""),
    # Drone Projects
    ("drone-project", "Hexacopter Fire Fighting Drone", "DJI-powered hexacopter with fire extinguishing ball system for firefighting operations.", img("d89d85_810810afe9214d1eb89b4bf5018682fa")),
    ("drone-project", "Solar Charging Quadcopter", "Quadcopter drone with self solar charging.", img("d89d85_3296f027a0854ad1a9c5789276e1d84a")),
    # Biomedical Projects
    ("biomedical-project", "Obstacle Detection Glasses", "Obstacle detection glasses for blind people.", img("d89d85_ae23ec2eb441429c96ce41e0adb793be")),
    ("biomedical-project", "Smart Blind Stick", "Smart blind stick with GPS and GSM technology.", ""),
    ("biomedical-project", "IoT Health Monitoring Kit", "Wearable health monitoring kit with IoT dashboard.", ""),
    # Mechanical Projects
    ("mechanical-project", "Fire Fighting Robot Car", "Fire detecting and fighting robot car.", img("d89d85_2cc4baa06083448f84fa0acf239b9dc8")),
    ("mechanical-project", "360° Fire Exhausting System", "All-direction fire exhaust and suppression system.", ""),
    ("mechanical-project", "Agriculture Robot", "Robotic platform for farm operations.", ""),
    ("mechanical-project", "Laser Engraving Machine", "CNC based laser engraving build.", ""),
    ("mechanical-project", "Automatic Bottle Filling Machine", "IoT based automatic water bottle filling machine.", ""),
    # Diploma Projects
    ("diploma-project", "Wireless Notice Board", "Wireless notice board using GSM and Arduino.", ""),
    ("diploma-project", "Industrial Temperature Control", "Temperature control system for industry.", ""),
    ("diploma-project", "Elevator Overload Alert", "Overload alert system in automatic elevator with microcontroller.", ""),
    ("diploma-project", "GSM Home Automation", "GSM based home automation system.", ""),
    # Degree Projects
    ("degree-project", "Induction Motor Fault Detection", "Fault detection in induction motor using microcontroller.", ""),
    ("degree-project", "Android Motor Speed Control", "Android-based speed control of induction motor.", ""),
    ("degree-project", "Highway Speed Violation Detection", "Speed limit violation detecting on highways.", ""),
    ("degree-project", "PV Panel Monitoring", "Monitoring and measurement of PV panels and solar energy.", ""),
    ("degree-project", "Solar Home Inverter Design", "Solar inverter design for homes.", ""),
]

async def main():
    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = client[os.environ["DB_NAME"]]
    added, skipped = 0, 0
    for category, title, description, image in CATALOGUE:
        exists = await db.projects.find_one({"category": category, "title": {"$regex": f"^{title}$", "$options": "i"}})
        if exists:
            skipped += 1
            continue
        await db.projects.insert_one({
            "id": str(uuid.uuid4()), "category": category, "title": title,
            "description": description, "price_hint": "", "image": image,
            "imported": True, "created_at": datetime.now(timezone.utc).isoformat(),
        })
        added += 1
    total = await db.projects.count_documents({})
    print(f"added={added} skipped={skipped} total={total}")
    client.close()

asyncio.run(main())
