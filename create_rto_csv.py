import csv
import os

os.makedirs("tn_license/csv", exist_ok=True)

rto_data = [
    ["RTO_Code", "RTO_Name", "District", "More_Info"],
    ["TN01", "RTO Chennai Central", "Chennai", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-chennai-(-central-)/tn-01"],
    ["TN02", "RTO Chennai North West", "Chennai", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-chennai-(-north-west-)/tn-02"],
    ["TN03", "RTO Chennai North East", "Chennai", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-chennai-(-north-east-),/tn-03"],
    ["TN04", "RTO Chennai East", "Chennai", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-chennai-(-east-)/tn-04"],
    ["TN05", "RTO Chennai North", "Chennai", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-chennai-(-north-)/tn-05"],
    ["TN06", "RTO Chennai South East", "Chennai", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-chennai-(-south-east-)/tn-06"],
    ["TN07", "RTO Chennai South", "Chennai", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-chennai-(-south-)/tn-07"],
    ["TN09", "RTO Chennai West", "Chennai", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-chennai-(-west-)/tn-09"],
    ["TN10", "RTO Chennai South West", "Chennai", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-chennai-(-south-west-)/tn-10"],
    ["TN11", "RTO Tambaram", "Chennai", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-office,-tambaram/tn-11"],
    ["TN12", "RTO Poonamalee", "Chennai", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-poonamalee/tn-12"],
    ["TN13", "RTO Ambattur", "Chennai", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-ambattur/tn-13"],
    ["TN14", "RTO Sholinganallur", "Chennai", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-sholinganallur/tn-14"],
    ["TN18", "RTO Redhills", "Chennai", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-redhills/tn-18"],
    ["TN19", "RTO Chengalpattu", "Chengalpattu", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-chengalpattu/tn-19"],
    ["TN20", "RTO Thiruvallur", "Thiruvallur", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-thiruvallur/tn-20"],
    ["TN21", "RTO Kancheepuram", "Kancheepuram", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-kancheepuram/tn-21"],
    ["TN22", "RTO Meenambakkam", "Chennai", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-meenambakkam/tn-22"],
    ["TN23", "RTO Vellore", "Vellore", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-vellore/tn-23"],
    ["TN24", "RTO Krishnagiri", "Krishnagiri", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-krishnagiri/tn-24"],
    ["TN25", "RTO Tiruvanamalai", "Tiruvannamalai", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-tiruvanamalai/tn-25"],
    ["TN28", "RTO Namakkal North", "Namakkal", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-namakkal-north/tn-28"],
    ["TN29", "RTO Dharmapuri", "Dharmapuri", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-dharmapuri/tn-29"],
    ["TN30", "RTO Salem West", "Salem", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-(-salem-west-)/tn-30"],
    ["TN31", "RTO Cuddalore", "Cuddalore", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-cudalore/tn-31"],
    ["TN32", "RTO Villupuram", "Villupuram", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-villupuram/tn-32"],
    ["TN33", "RTO Erode East", "Erode", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-erode-east/tn-33"],
    ["TN37", "RTO Coimbatore South", "Coimbatore", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-coimbatore-(-south-)/tn-37"],
    ["TN38", "RTO Coimbatore North", "Coimbatore", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-coimbatore-(-north-)/tn-38"],
    ["TN39", "RTO Tirupur North", "Tirupur", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-tirupur-(-north-)/tn-39"],
    ["TN43", "RTO Ooty", "Nilgiris", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-ooty/tn-43"],
    ["TN45", "RTO Tiruchirappalli West", "Tiruchirappalli", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-tiruchirappalli-west/tn-45"],
    ["TN47", "RTO Karur", "Karur", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-karur/tn-47"],
    ["TN49", "RTO Thanjavur", "Thanjavur", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto,-tanjavur/tn-49"],
    ["TN51", "RTO Nagapattinam", "Nagapattinam", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-nagapattinam/tn-51"],
    ["TN54", "RTO Salem East", "Salem", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-salem-(-east-)/tn-54"],
    ["TN55", "RTO Pudukottai", "Pudukkottai", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-pudukottai/tn-55"],
    ["TN57", "RTO Dindigul", "Dindigul", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-dindigul/tn-57"],
    ["TN58", "RTO Madurai South", "Madurai", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-madurai-(-south-)/tn-58"],
    ["TN59", "RTO Madurai North", "Madurai", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-madurai-(-north-)/tn-59"],
    ["TN63", "RTO Sivagangai", "Sivaganga", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-sivagangai/tn-63"],
    ["TN65", "RTO Ramanathapuram", "Ramanathapuram", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-ramanathapuram/tn-65"],
    ["TN67", "RTO Virudhunagar", "Virudhunagar", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-virudhunagar/tn-67"],
    ["TN68", "RTO Kumbakonam", "Thanjavur", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-kumbakonam/tn-68"],
    ["TN69", "RTO Tuticorin", "Thoothukudi", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-tuticorin/tn-69"],
    ["TN70", "RTO Hosur", "Krishnagiri", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-hosur/tn-70"],
    ["TN72", "RTO Tirunelveli", "Tirunelveli", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-tirunelveli/tn-72"],
    ["TN73", "RTO Ranipet", "Ranipet", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-ranipet/tn-73"],
    ["TN74", "RTO Nagercoil", "Kanyakumari", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-nagercoil/tn-74"],
    ["TN85", "RTO Kundrathur", "Chennai", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-kundrathur/tn-85"],
    ["TN86", "RTO Erode West", "Erode", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-erode-west/tn-86"],
    ["TN88", "RTO Namakkal South", "Namakkal", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-namakkal-south/tn-88"],
    ["TN90", "RTO Salem South", "Salem", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-salem-south/tn-90"],
    ["TN99", "RTO Coimbatore West", "Coimbatore", "https://rtovehicleinfohub.in/rto-office-details/tamil-nadu/rto-coimbatore-west/tn-99"],
]

with open("tn_license/csv/rto_offices.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerows(rto_data)

print(f"✅ CSV created with {len(rto_data)-1} RTO offices!")