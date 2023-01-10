import time
import requests
requests.packages.urllib3.disable_warnings() 

# Tesla API doc : https://github.com/vloschiavo/powerwall2#post-apiloginbasic

class PowerwallMonitor:
    def __init__(self, address:str, email:str, password:str) -> None:
        self.address: str = address
        self.email: str = email
        self.password: str = password
        self.token: str = None
    
    def get_token(self):
        if self.token == None:
            url = f"https://{self.address}/api/login/Basic"
            body = {
                        "username": "customer",
                        "email": self.email,
                        "password": self.password,
                        "force_sm_off": False
                    }

            res = requests.post(url, json=body, verify=False)
            if res.ok:
                data = res.json()
                if 'token' in data:
                    self.token = data['token']

    def get_charge(self) -> None:
        self.get_token()
        
        if self.token != None:
            url = f"https://{self.address}/api/system_status/soe"
            headers =   {
                            'Authorization': f"Bearer {self.token}" 
                        }

            res = requests.get(url, headers=headers, verify=False)
            if res.ok:
                data = res.json()
                if 'percentage' in data:
                    return data['percentage']
        return None