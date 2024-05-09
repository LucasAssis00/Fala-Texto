from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

# Inicializa o navegador
driver = webdriver.Edge()  # Você precisa do driver do Chrome ou de outro navegador que desejar
#driver = webdriver.ChromiumEdge()
# Abre a página de login da rede social
driver.get("https://docs.google.com/forms/d/1UZkASiSkVhUnS-ppKGi7mStAF14UAw5zL_YIvHMzIjM/edit")
time.sleep(1)
# Encontra os campos de usuário e senha e os preenche
'''
button = driver.find_element("xpath", '//*[@id="loginSignup"]/li[1]/a')
button.click()
time.sleep(5)
'''
#//*[@id="loginSignup"]/li[1]/a
#usuario = driver.find_element_by_name("txtEmail")  # Substitua "usuario" pelo nome do campo de usuário
info1 = "oi"
campo1 = driver.find_element("xpath", '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[1]/div/div/div[2]/div/div[1]/div/div[1]/input')  # Substitua "usuario" pelo nome do campo de usuário
campo1.send_keys(info1)
time.sleep(1)
info2 = "oioi"
campo2 = driver.find_element("xpath", '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/input')  # Substitua "usuario" pelo nome do campo de usuário
campo2.send_keys(info2)
# Insira aqui o seu usuário e senha
#usuario.send_keys(Keys.RETURN)
time.sleep(1)
info3 = "oioioi"
campo3 = driver.find_element("xpath", '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[3]/div/div/div[2]/div/div[1]/div/div[1]/input')  # Substitua "usuario" pelo nome do campo de usuário
campo3.send_keys(info3)
time.sleep(1)
info4 = "oioioioi"
campo4 = driver.find_element("xpath", '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[4]/div/div/div[2]/div/div[1]/div/div[1]/input')  # Substitua "usuario" pelo nome do campo de usuário
campo4.send_keys(info4)
time.sleep(1)
info5 = "oioioioioi"
campo5 = driver.find_element("xpath", '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[5]/div/div/div[2]/div/div[1]/div/div[1]/input')  # Substitua "usuario" pelo nome do campo de usuário
campo5.send_keys(info5)
'''
senha = driver.find_element("xpath", '//*[@id="password"]')  # Substitua "senha" pelo nome do campo de senha
senha.send_keys(password)

# Submete o formulário de login
senha.send_keys(Keys.RETURN)
'''
#/html/body/div/div[3]/form/div[2]/div/div[3]/div[1]/div[1]/div/span/span
time.sleep(1)
#button = driver.find_element("xpath", '/html/body/div/div[3]/form/div[2]/div/div[3]/div[1]/div[1]/div/span/span')
button = driver.find_element("xpath", '//*[@id="mG61Hd"]/div[2]/div/div[3]/div[1]/div[1]/div/span/span')
button.click()


# Aguarde um momento para o login ser concluído
time.sleep(1)

# Feche o navegador
driver.quit()
