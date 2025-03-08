from cereal import car
from openpilot.selfdrive.car.chrysler.values import RAM_CARS

GearShifter = car.CarState.GearShifter
VisualAlert = car.CarControl.HUDControl.VisualAlert

def create_mango_hud(packer, apa_active, apa_fault, enabled, steer_type):
  # LKAS_HUD 0x2a6 (678) Controls what lane-keeping icon is displayed.

  color = 1  # default values are for park or neutral in 2017 are 0 0, but trying 1 1 for 2019
  lines = 1

  # had color = 1 and lines = 1 but trying 2017 hybrid style for now.
  if enabled and apa_active:
      color = 2  # control active, display green.
  if apa_fault:
    color = 3
  values = {
    "LKAS_ICON_COLOR": color,  # byte 0, last 2 bits
    "LKAS_LANE_LINES": lines,  # byte 2, last 4 bits
    "STEER_TYPE": steer_type,
    }
  return packer.make_can_msg("DAS_6", 0, values)  # 0x2a6

#def create_lkas_hud(packer, CP, lat_active, hud_alert, hud_count, car_model, auto_high_beam, lat_available, cruise_available):
  # LKAS_HUD - Controls what lane-keeping icon is displayed

  # == Color ==
  # 0 hidden?
  # 1 white
  # 2 green
  # 3 ldw

  # == Lines ==
  # 03 white Lines
  # 04 grey lines
  # 09 left lane close
  # 0A right lane close
  # 0B left Lane very close
  # 0C right Lane very close
  # 0D left cross cross
  # 0E right lane cross

  # == Alerts ==
  # 0 Normal
  # 6 place hands on wheel
  # 7 lane departure place hands on wheel

#  if hud_alert == VisualAlert.ldw:
#    color = 3
#    lines = 0
#    alerts = 7
#  elif hud_alert == VisualAlert.steerRequired:
#    color = 3
#    lines = 0
#    alerts = 6
#  else:
#    color = 2 if lat_active else 3 if lat_available else 1 if cruise_available else 0
#    lines = 3 if lat_active else 0
#    alerts = 1 if hud_count < (1 * 4) else 0

#  values = {
#    "LKAS_ICON_COLOR": color,
#    "CAR_MODEL": car_model,
#    "LKAS_LANE_LINES": lines,
#    "LKAS_ALERTS": alerts,
#  }

#  if CP.carFingerprint in RAM_CARS:
#    values['AUTO_HIGH_BEAM_ON'] = auto_high_beam

#  return packer.make_can_msg("DAS_6", 0, values)

  # LKAS_HUD 0x2a6 (678) Controls what lane-keeping icon is displayed.

  color = 1  # default values are for park or neutral in 2017 are 0 0, but trying 1 1 for 2019
  lines = 1
  alerts = 0

  if hud_count < (1 * 4):  # first 3 seconds, 4Hz
    alerts = 1
  # had color = 1 and lines = 1 but trying 2017 hybrid style for now.
  if gear in (GearShifter.drive, GearShifter.reverse, GearShifter.low):
    if lkas_active:
      color = 2  # control active, display green.
      lines = 6
    else:
      color = 1  # control off, display white.
      lines = 1

  values = {
    "LKAS_ICON_COLOR": color,  # byte 0, last 2 bits
    "LKAS_LANE_LINES": lines,  # byte 2, last 4 bits
    "LKAS_ALERTS": alerts,  # byte 3, last 4 bits
    "STEER_TYPE": steer_type,
    }

  return packer.make_can_msg("DAS_6", 0, values)  # 0x2a6


#def create_lkas_command(packer, CP, apply_steer, lkas_control_bit, wp_active):
  # LKAS_COMMAND Lane-keeping signal to turn the wheel
#  enabled_val = 2 if CP.carFingerprint in RAM_CARS else 1
#  values = {
#    "WP_CONTROL": 1,
#    "WP_ACTIVE": 1 if wp_active else 0,
#    "STEERING_TORQUE": apply_steer,
#    "LKAS_CONTROL_BIT": enabled_val if lkas_control_bit else 0,
#  }
#  return packer.make_can_msg("LKAS_COMMAND", 0, values)

def create_lkas_command(packer, apply_steer, lkas_active, counter):
  # LKAS_COMMAND 0x292 (658) Lane-keeping signal to turn the wheel.
  values = {
    "STEERING_TORQUE": apply_steer,
    "LKAS_CONTROL_BIT": lkas_active,
    "COUNTER": counter,
  }
  return packer.make_can_msg("LKAS_COMMAND", 0, values)

def create_lkas_heartbit(packer, lkas_disabled, lkasHeartbit):
  # LKAS_HEARTBIT (697) LKAS heartbeat
  values = lkasHeartbit.copy()  # forward what we parsed
  values["LKAS_DISABLED"] = 1 if lkas_disabled else 0
  return packer.make_can_msg("LKAS_HEARTBIT", 0, values)

def create_wheel_buttons_command(packer, bus, frame, buttons):
  # WHEEL_BUTTONS (571) Message sent
  values = {
    "COUNTER": frame % 0x10,
  }

  for b in buttons:
    if b is not None:
      values[b] = 1

  return packer.make_can_msg("CRUISE_BUTTONS", bus, values)

def das_3_command(packer, counter_offset, go, torque_req, torque, max_gear, stop, brake, brake_prep, das_3):
  values = das_3.copy()  # forward what we parsed
  values['ACC_AVAILABLE'] = 1
  values['ACC_ACTIVE'] = 1
  values['COUNTER'] = (das_3['COUNTER'] + counter_offset) % 0x10

  if go is not None:
    values['ACC_GO'] = go

  if stop is not None:
    values['ACC_STANDSTILL'] = stop

  if brake is not None:
    values['ACC_DECEL_REQ'] = 1
    values['ACC_DECEL'] = brake
    values['ACC_BRK_PREP'] = brake_prep

  if torque is not None:
    values['ENGINE_TORQUE_REQUEST_MAX'] = torque_req
    values['ENGINE_TORQUE_REQUEST'] = torque

  if max_gear is not None:
    values['GR_MAX_REQ'] = max_gear

  return packer.make_can_msg("DAS_3", 0, values)

def das_5_command(packer, counter_offset, gas, das_5):
  values = das_5.copy()  # forward what we parsed
  values['COUNTER'] = (das_5['COUNTER'] + counter_offset) % 0x10

  if gas is not None:
    values['WHEEL_TORQUE_REQUEST_ACTIVE'] = 1
    values['WHEEL_TORQUE_REQUEST'] = gas

  return packer.make_can_msg("DAS_5", 0, values)

def acc_log(packer, adjustment, aTarget, vTarget, aEgo):
  values = {
    'OP_A_TARGET': aTarget,
    'OP_V_TARGET': vTarget,
    'ADJUSTMENT': adjustment,
    'A_EGO': aEgo
  }
  return packer.make_can_msg("ACC_LOG", 0, values)
