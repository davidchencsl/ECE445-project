import React, { useEffect, useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View, TextInput } from 'react-native';
import { ListItem } from 'react-native-elements'
import Button from './components/Button';
import AxisPad from './components/AxisPad';
import axios from 'axios';
import _ from 'lodash';

const [IP, PORT] = ["10.0.0.2", 6969];

export default function App() {


  const [connectedDevice, setConnectedDevice] = useState({ ip: IP, port: PORT });

  const [controls, setControls] = useState({
    max_speed: 1,
    angle: 0,
    speed: 0,
    l_speed: 0,
    r_speed: 0,
    l_pwm: 0,
    r_pwm: 0,
    distance: 0
  });

  const [connected, setConnected] = useState(true);

  useEffect(() => {
    const interval = setInterval(() => {
      const url = `http://${connectedDevice.ip}:${connectedDevice.port}`;
      axios.get(`${url}/api/stats`)
        .then(res => {
          setControls({ ...controls, l_speed: res.data.l_speed, r_speed: res.data.r_speed, distance: res.data.distance, l_pwm: res.data.l_pwm, r_pwm: res.data.r_pwm });
          setConnected(true);
        })
        .catch(err => {
          console.log(err);
          setConnected(false);
        });
    }, 100);
    return () => clearInterval(interval);
  }, []);


  return (
    <View style={styles.container}>
      <View style={{ flex: 0.1 }}></View>
      <View style={{ flex: 0.1 }}>
        <Text style={styles.titleText}>AutoLUG</Text>
      </View>
      <View style={{ flex: 0.8, width: '100%' }}>
        <Text style={styles.titleText}>Measured L Speed: {controls.l_speed.toFixed(2)}m/s</Text>
        <Text style={styles.titleText}>Measured R Speed: {controls.r_speed.toFixed(2)}m/s</Text>
        <Text style={styles.titleText}>Measured Distance: {controls.distance.toFixed(2)}m</Text>
        <Text style={styles.titleText}>Deviation Angle: {controls.angle.toFixed(2)} degree</Text>
        <Text style={styles.titleText}>Desired Speed: {controls.speed.toFixed(2)}m/s</Text>
        <Text style={styles.titleText}>L PWM: {controls.l_pwm}</Text>
        <Text style={styles.titleText}>R PWM: {controls.r_pwm}</Text>
        <View style={{ flexDirection: 'row' }}>
          <Text style={styles.titleText}>Max Speed (m/s): </Text>
          <TextInput
            style={[styles.titleText, { backgroundColor: 'lightgray', borderRadius: 5 }]}
            placeholder={"Enter Max Speed"}
            onChangeText={(text) => {
              var speed = 0;
              if (isNaN(text))
                speed = 0;
              speed = parseFloat(text);
              if (speed < 0 || speed > 2)
                speed = 0;
              setControls({ ...controls, max_speed: speed })
            }}
          />
        </View>
      </View>
      <View style={{ flex: 0.15 }}>
        <Text style={styles.titleText} >{connected ? `Connected to ${connectedDevice.ip}:${connectedDevice.port}` : "Connection Failed"}</Text>
      </View>
      <View style={{ flex: 0.3 }}>
        <Button title='   STOP   ' />
      </View>
      <View style={{ flex: 1 }}>
        <AxisPad
          resetOnRelease={true}
          autoCenter={true}
          onValue={
            _.debounce(
              ({ x, y }) => {
                y = -y;
                var magnitude = Math.sqrt(x * x + y * y);
                var angle = Math.atan2(x, y) * 180 / Math.PI;
                magnitude = magnitude > 1 ? 1 : magnitude;
                angle = (x == 0 && y == 0) ? 0 : angle;
                setControls({ ...controls, angle: angle, speed: magnitude * controls.max_speed });
                const url = `http://${connectedDevice.ip}:${connectedDevice.port}`;
                axios.post(`${url}/api/controls`, {deviation_angle: controls.angle, desired_speed: controls.speed});
              }, 100)
          }>
        </AxisPad>
      </View>
      <StatusBar style="auto" />
    </View >
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  baseText: {
    fontFamily: 'Cochin',
  },
  titleText: {
    fontSize: 20,
    fontWeight: 'bold',
  },
});
