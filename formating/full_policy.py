def extract_policy_fields(data):
    """
    Extract all important policy fields from the AMS360 PolicyGet response.
    """

    try:
        policy = data["s:Envelope"]["s:Body"]["PolicyGetResponse"]["PolicyGetResult"]["a:Policy"]
    except KeyError:
        raise ValueError("Invalid AMS360 PolicyGet response structure")

    # Helper to fetch fields safely
    def get(field, default=None):
        return policy.get(field, default)

    # Transaction list (latest transaction)
    transactions = policy.get("a:TransactionList", {}).get("a:PolicyTransaction", [])
    if isinstance(transactions, dict):
        transactions = [transactions]
    latest_txn = sorted(transactions, key=lambda x: x.get("a:TransactionEffectiveDate", ""), reverse=True)[0] if transactions else {}

    # Premium list (latest premium record)
    premiums = policy.get("a:TransactionPremiumList", {}).get("a:PolicyTransactionPremium", [])
    if isinstance(premiums, dict):
        premiums = [premiums]
    latest_premium = sorted(premiums, key=lambda x: x.get("a:TransactionEffectiveDate", ""), reverse=True)[0] if premiums else {}

    # Personnel (Executive & CSR)
    personnel = policy.get("a:PersonnelList", {}).get("a:PolicyPersonnel", [])
    if isinstance(personnel, dict):
        personnel = [personnel]

    account_exec = next((p.get("a:EmployeeCode") for p in personnel if p.get("a:EmployeeType") == "P"), None)
    account_rep = next((p.get("a:EmployeeCode") for p in personnel if p.get("a:EmployeeType") == "R"), None)

    # Line of Business
    lob = policy.get("a:LineOfBusinessList", {}).get("a:PolicyLineOfBusiness", {})
    if isinstance(lob, list):
        lob = lob[0]

    # Final cleaned result dictionary
    return {
        "PolicyId": get("a:PolicyId"),
        "PolicyNumber": get("a:PolicyNumber"),
        "CustomerId": get("a:CustomerId"),

        # Business info
        "PolicyTypeOfBusiness": get("a:PolicyTypeOfBusiness"),
        "PolicySubType": get("a:PolicySubType"),
        "CompanyType": get("a:CompanyType"),

        # Dates
        "EffectiveDate": get("a:PolicyEffectiveDate"),
        "ExpirationDate": get("a:PolicyExpirationDate"),
        "IsNewPolicy": get("a:IsNewPolicy"),

        # Premiums
        "FullTermPremium": get("a:FullTermPremium"),
        "IsFinanced": get("a:IsFinanced"),
        "BillMethod": get("a:BillMethod"),

        # Line of Business
        "LineOfBusiness": lob.get("a:PolicyLineOfBusiness"),
        "LineDescription": lob.get("a:PolicyLineOfBusiness"),
        "LineOfBusinessId": lob.get("a:LineOfBusinessId"),

        # Assigned Personnel
        "AccountExecutiveCode": account_exec,
        "AccountRepCode": account_rep,

        # Latest transaction
        "LatestTransactionType": latest_txn.get("a:TransactionType"),
        "LatestTransactionDescription": latest_txn.get("a:TransactionDescription"),
        "LatestTransactionDate": latest_txn.get("a:TransactionEffectiveDate"),

        # Latest Premium Breakdown
        "LatestPremium": latest_premium.get("a:Premium"),
        "LatestFullTermPremium": latest_premium.get("a:FullTermPremium"),
        "LatestWritingCompanyCode": latest_premium.get("a:WritingCompanyCode"),
    }

def extract_customer_fields(data):
    try:
        customer = (
            data.get("s:Envelope", {})
                .get("s:Body", {})
                .get("CustomerGetByIdResponse", {})
                .get("CustomerGetByIdResult", {})
                .get("a:Customer", {})
        )
    except Exception:
        return {"error": "Invalid AMS360 structure"}

    # Helper to get fields safely
    def get(key):
        return customer.get(key, None)

    extracted = {
        "CustomerId": get("a:CustomerId"),
        "CustomerNumber": get("a:CustomerNumber"),
        "CustomerType": get("a:CustomerType"),

        # Personal Information
        "FirstName": get("a:FirstName"),
        "MiddleName": get("a:MiddleName"),
        "LastName": get("a:LastName"),
        "DateOfBirth": get("a:DateOfBirth"),
        "MaritalStatus": get("a:MaritalStatus"),

        # Contact Information
        "Email": get("a:Email"),
        "CellAreaCode": get("a:CellAreaCode"),
        "CellPhone": get("a:CellPhone"),
        "BusinessPhone": get("a:BusinessPhone"),
        "HomePhone": get("a:HomePhone"),

        # Address
        "AddressLine1": get("a:AddressLine1"),
        "AddressLine2": get("a:AddressLine2"),
        "City": get("a:City"),
        "State": get("a:State"),
        "ZipCode": get("a:ZipCode"),
        "Country": get("a:Country"),

        # Agency Info
        "AccountExecCode": get("a:AccountExecCode"),
        "AccountRepCode": get("a:AccountRepCode"),

        # Status Flags
        "IsActive": get("a:IsActive"),
        "IsPersonal": get("a:IsPersonal"),
        "IsCommercial": get("a:IsCommercial"),

        # Metadata
        "DateCustomerAdded": get("a:DateCustomerAdded"),
    }

    return extracted


def extract_policy_list(payload: dict) -> list:
    """
    Extract policy list from AMS360 PolicyGetListByCustomerIdResponse.
    Safely handles missing keys and nested structures.
    """

    try:
        policies = (
            payload.get("s:Envelope", {})
            .get("s:Body", {})
            .get("PolicyGetListByCustomerIdResponse", {})
            .get("PolicyGetListByCustomerIdResult", {})
            .get("a:PolicyInfoList", {})
            .get("a:PolicyInfo", [])
        )
    except Exception:
        return []

    # Ensure it's a list
    if isinstance(policies, dict):
        policies = [policies]

    cleaned_list = []

    for p in policies:
        cleaned_list.append({
            "CompanyType": p.get("a:CompanyType"),
            "CustomerId": p.get("a:CustomerId"),
            "IsMultiEntity": p.get("a:IsMultiEntity"),
            "PolicyEffectiveDate": p.get("a:PolicyEffectiveDate"),
            "PolicyExpirationDate": p.get("a:PolicyExpirationDate"),
            "PolicyId": p.get("a:PolicyId"),
            "PolicyNumber": p.get("a:PolicyNumber"),
            "PolicySubType": p.get("a:PolicySubType"),
            "PolicyTypeOfBusiness": p.get("a:PolicyTypeOfBusiness"),
            "PolicyStatus": p.get("a:PolicyStatus"),
            "WritingCompanyCode": p.get("a:WritingCompanyCode"),
        })

    return cleaned_list



# ---------------------------
# Example use:
# ---------------------------

# result = extract_customer_fields(api_response_dict)
# print(result)


# ----------------------------
# Example Usage
# ----------------------------

# result = extract_policy_fields(your_json_data)
# print(result)
