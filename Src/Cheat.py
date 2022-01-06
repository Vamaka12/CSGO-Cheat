import math
import pymem
import time
import requests
import keyboard
from math import sqrt, pi, atan


def normalizeAngles(viewAngleX, viewAngleY):
    if viewAngleX > 89:
        viewAngleX -= 360
    if viewAngleX > -89:
        viewAngleX += 360
    if viewAngleY > 180:
        viewAngleY -= 360
    if viewAngleY < 180:
        viewAngleY += 360
    return viewAngleX, viewAngleY


def checkangles(x, y):
    if x > 89:
        return False
    elif x < -89:
        return False
    elif y > 360:
        return False
    elif y < -360:
        return False
    else:
        return True


def nanchecker(first, second):
    if math.isnan(first) or math.isnan(second):
        return False
    else:
        return True


def calc_distance(current_x, current_y, new_x, new_y):
    distancex = new_x - current_x
    if distancex < -89:
        distancex += 360
    elif distancex > 89:
        distancex -= 360
    if distancex < 0.0:
        distancex = -distancex

    distancey = new_y - current_y
    if distancey < -180:
        distancey += 360
    elif distancey > 180:
        distancey -= 360
    if distancey < 0.0:
        distancey = -distancey
    return distancex, distancey


def calcangle(localpos1, localpos2, localpos3, enemypos1, enemypos2, enemypos3):
    try:
        delta_x = localpos1 - enemypos1
        delta_y = localpos2 - enemypos2
        delta_z = localpos3 - enemypos3
        hyp = sqrt(delta_x * delta_x + delta_y * delta_y + delta_z * delta_z)
        x = atan(delta_z / hyp) * 180 / pi
        y = atan(delta_y / delta_x) * 180 / pi
        if delta_x >= 0.0:
            y += 180.0
        return x, y
    except:
        pass


def Cheat():
    switch = 0
    player = pm.read_int(client + dwLocalPlayer)
    engine_pointer = pm.read_int(engine + dwClientState)
    localTeam = pm.read_int(player + m_iTeamNum)
    aimfov = 120
    rgbT = [233, 233, 0]
    rgbCT = [0, 51, 255]
    print(">> Cheat Activated")
    while True:
        try:

            # AIM
            target = None
            olddistx = 111111111111
            olddisty = 111111111111

            for i in range(1, 32):
                entity = pm.read_int(client + dwEntityList + i * 0x10)

                if entity:
                    try:
                        entity_team_id = pm.read_int(entity + m_iTeamNum)
                        entity_hp = pm.read_int(entity + m_iHealth)
                        entity_dormant = pm.read_int(entity + m_bDormant)
                    except:
                        print("Finds Player info once")

                    if localTeam != entity_team_id and entity_hp > 0:
                        entity_bones = pm.read_int(entity + m_dwBoneMatrix)
                        localpos_x_angles = pm.read_float(engine_pointer + dwClientState_ViewAngles)
                        localpos_y_angles = pm.read_float(engine_pointer + dwClientState_ViewAngles + 0x4)
                        localpos_z_angles = pm.read_float(engine_pointer + m_vecViewOffset + 0x8)
                        localpos1 = pm.read_float(player + m_vecOrigin)
                        localpos2 = pm.read_float(player + m_vecOrigin + 4)
                        localpos3 = pm.read_float(player + m_vecOrigin + 8) + localpos_z_angles

                        try:
                            entitypos_x = pm.read_float(entity_bones + 0x30 * 8 + 0xC)
                            entitypos_y = pm.read_float(entity_bones + 0x30 * 8 + 0x1C)
                            entitypos_z = pm.read_float(entity_bones + 0x30 * 8 + 0x2C)
                        except:
                            continue

                        X, Y = calcangle(localpos1, localpos2, localpos3, entitypos_x, entitypos_y, entitypos_z)
                        newdist_x, newdist_y = calc_distance(localpos_x_angles, localpos_y_angles, X, Y)

                        if newdist_x < olddistx and newdist_y < olddisty and newdist_x <= aimfov and newdist_y <= aimfov:
                            olddistx, olddisty = newdist_x, newdist_y
                            target, target_hp, target_dormant = entity, entity_hp, entity_dormant
                            target_x, target_y, target_z = entitypos_x, entitypos_y, entitypos_z

                    if keyboard.is_pressed("v") and player:

                        if target and target_hp > 0 and not target_dormant:
                            x, y = calcangle(localpos1, localpos2, localpos3, target_x, target_y, target_z)
                            normalize_x, normalize_y = normalizeAngles(x, y)

                            pm.write_float(engine_pointer + dwClientState_ViewAngles, normalize_x)
                            pm.write_float(engine_pointer + dwClientState_ViewAngles + 0x4, normalize_y)

            # WH
            glow_manager = pm.read_int(client + dwGlowObjectManager)

            for i in range(1, 32):
                entity = pm.read_int(client + dwEntityList + i * 0x10)

                if entity:
                    entity_team_id = pm.read_int(entity + m_iTeamNum)
                    entity_glow = pm.read_int(entity + m_iGlowIndex)

                    if entity_team_id == 2:  # Terrorist
                        pm.write_float(glow_manager + entity_glow * 0x38 + 0x4, float(1))  # R
                        pm.write_float(glow_manager + entity_glow * 0x38 + 0x8, float(1))  # G
                        pm.write_float(glow_manager + entity_glow * 0x38 + 0xC, float(0))  # B
                        pm.write_float(glow_manager + entity_glow * 0x38 + 0x10, float(1))  # Alpha
                        pm.write_int(glow_manager + entity_glow * 0x38 + 0x24, 1)  # Enable glow

                    elif entity_team_id == 3:  # Counter-terrorist
                        pm.write_float(glow_manager + entity_glow * 0x38 + 0x4, float(0))  # R
                        pm.write_float(glow_manager + entity_glow * 0x38 + 0x8, float(0))  # G
                        pm.write_float(glow_manager + entity_glow * 0x38 + 0xC, float(1))  # B
                        pm.write_float(glow_manager + entity_glow * 0x38 + 0x10, float(1))  # Alpha
                        pm.write_int(glow_manager + entity_glow * 0x38 + 0x24, 1)  # Enable glow

            # no flash
            if player:
                flash_value = player + m_flFlashMaxAlpha
                if flash_value:
                    pm.write_float(flash_value, float(0))

            # from 3 person view
            if keyboard.is_pressed("x") and switch == 0:
                time.sleep(0.5)
                pm.write_int(player + m_iObserverMode, 1)
                switch = 1

            elif keyboard.is_pressed("x") and switch == 1:
                time.sleep(0.5)
                pm.write_int(player + m_iObserverMode, 0)
                switch = 0

            # chams
            for i in range(32):
                entity = pm.read_int(client + dwEntityList + i * 0x10)

                if entity:

                    entity_team_id = pm.read_int(entity + m_iTeamNum)

                    if entity_team_id == 2:  # T
                        pm.write_int(entity + m_clrRender, (rgbT[0]))  # R
                        pm.write_int(entity + m_clrRender + 0x1, (rgbT[1]))  # G
                        pm.write_int(entity + m_clrRender + 0x2, (rgbT[2]))  # B

                    elif entity_team_id == 3:  # CT
                        pm.write_int(entity + m_clrRender, (rgbCT[0]))  # R
                        pm.write_int(entity + m_clrRender + 0x1, (rgbCT[1]))  # G
                        pm.write_int(entity + m_clrRender + 0x2, (rgbCT[2]))  # B


                    else:
                        pass

            # TriggerBot
            entity_id = pm.read_int(player + m_iCrosshairId)
            entity = pm.read_int(client + dwEntityList + (entity_id - 1) * 0x10)

            entity_team = pm.read_int(entity + m_iTeamNum)
            player_team = pm.read_int(player + m_iTeamNum)

            if entity_id > 0 and entity_id <= 64 and player_team != entity_team:
                pm.write_int(client + dwForceAttack, 6)


        except pymem.exception.MemoryReadError:
            pass


print('>>> Cheat is Starting...')

offsets = 'https://raw.githubusercontent.com/frk1/hazedumper/master/csgo.json'
response = requests.get(offsets).json()

print('')
print('>>> Getting Offsets...')

dwSetClanTag = int(response["signatures"]["dwSetClanTag"])
dwGlowObjectManager = int(response["signatures"]["dwGlowObjectManager"])
dwEntityList = int(response["signatures"]["dwEntityList"])
m_iTeamNum = int(response["netvars"]["m_iTeamNum"])
m_iGlowIndex = int(response["netvars"]["m_iGlowIndex"])
dwLocalPlayer = int(response["signatures"]["dwLocalPlayer"])
dwForceJump = int(response["signatures"]["dwLocalPlayer"])
m_fFlags = int(response["netvars"]["m_fFlags"])
dwForceAttack = int(response["signatures"]["dwForceAttack"])
m_iCrosshairId = int(response["netvars"]["m_iCrosshairId"])
m_flFlashMaxAlpha = int(response["netvars"]["m_flFlashMaxAlpha"])
m_iObserverMode = int(response["netvars"]["m_iObserverMode"])
dwClientState = int(response["signatures"]["dwClientState"])
dwClientState_ViewAngles = int(response["signatures"]["dwClientState_ViewAngles"])
m_vecOrigin = int(response["netvars"]["m_vecOrigin"])
m_bDormant = int(response["signatures"]["m_bDormant"])
m_vecViewOffset = int(response["netvars"]["m_vecViewOffset"])
m_dwBoneMatrix = int(response["netvars"]["m_dwBoneMatrix"])
m_iHealth = int(response["netvars"]["m_iHealth"])
m_clrRender = int(response["netvars"]["m_clrRender"])

try:
    pm = pymem.Pymem("csgo.exe")
    client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll
    engine = pymem.process.module_from_name(pm.process_handle, "engine.dll").lpBaseOfDll
except:
    print("Can't Find process csgo.exe Did you run Csgo?")
    time.sleep(10)
    exit()

Cheat()
