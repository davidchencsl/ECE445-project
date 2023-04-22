import React, { useEffect, useState, useRef } from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View, TextInput, Image } from 'react-native';
import { ListItem } from 'react-native-elements'
import Button from './components/Button';
import AxisPad from './components/AxisPad';
import axios from 'axios';
import _ from 'lodash';

const [IP, PORT] = ["10.0.0.2", 6969];

export default function App() {

  const [connectedDevice, setConnectedDevice] = useState({ ip: IP, port: PORT });

  const [controls, setControls] = useState({
    angle: 0,
    speed: 0
  });

  const [stats, setStats] = useState({
    l_speed: 0,
    r_speed: 0,
    distance: 0,
    l_pwm: 0,
    r_pwm: 0,
    max_speed: 1,
    connected: false
  });

  const [mode, setMode] = useState('MANUAL');
  const [frame, setFrame] = useState('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADMAAAAzCAYAAAA6oTAqAAAAEXRFWHRTb2Z0d2FyZQBwbmdjcnVzaEB1SfMAAABQSURBVGje7dSxCQBACARB+2/ab8BEeQNhFi6WSYzYLYudDQYGBgYGBgYGBgYGBgYGBgZmcvDqYGBgmhivGQYGBgYGBgYGBgYGBgYGBgbmQw+P/eMrC5UTVAAAAABJRU5ErkJggg==');

  useEffect(() => {
    const interval = setInterval(() => {
      const url = `http://${connectedDevice.ip}:${connectedDevice.port}`;
      axios.get(`${url}/api/stats`)
        .then(res => {
          setStats({ ...stats, l_speed: res.data.l_speed, r_speed: res.data.r_speed, distance: res.data.distance, l_pwm: res.data.l_pwm, r_pwm: res.data.r_pwm, connected: true });
        })
        .catch(err => {
          console.log(err);
          setStats({ ...stats, connected: false });
        });
      if (mode !== 'MANUAL') {
        axios.get(`${url}/api/camera`)
          .then(res => {
            setFrame(res.data.image);
          })
      }
    }, 100);
    return () => clearInterval(interval);
  }, [mode]);

  const postControls = useRef(_.throttle((angle, speed) => {
    const url = `http://${connectedDevice.ip}:${connectedDevice.port}`;
    axios.post(`${url}/api/controls`, { deviation_angle: angle, desired_speed: speed });
  }, 100));


  return (
    <View style={styles.container}>
      <View style={{ flex: 0.1 }}></View>
      <View style={{ flex: 0.1 }}>
        <Text style={styles.titleText}>AutoLUG</Text>
      </View>
      <View style={{ flex: 0.45, width: '100%' }}>
        <Text style={styles.titleText}>Measured L Speed: {stats.l_speed.toFixed(2)}m/s</Text>
        <Text style={styles.titleText}>Measured R Speed: {stats.r_speed.toFixed(2)}m/s</Text>
        <Text style={styles.titleText}>Measured Distance: {stats.distance.toFixed(2)}m</Text>
        <Text style={styles.titleText}>Deviation Angle: {controls.angle.toFixed(2)} degree</Text>
        <Text style={styles.titleText}>Desired Speed: {controls.speed.toFixed(2)}m/s</Text>
        <Text style={styles.titleText}>L PWM: {stats.l_pwm}</Text>
        <Text style={styles.titleText}>R PWM: {stats.r_pwm}</Text>
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
              setStats({ ...stats, max_speed: speed })
            }}
          />
        </View>
      </View>
      <View style={{ flex: 0.1 }}>
        <Text style={styles.titleText} >{stats.connected ? `Connected to ${connectedDevice.ip}:${connectedDevice.port}` : "Connection Failed"}</Text>
      </View>
      <View style={{ flex: 0.15 }}>
        <Button title='   STOP   ' />
      </View>
      <View style={{ flex: 0.15 }}>
        <Button title={`${mode}`}
          onPress={() => {
            setMode(mode == 'MANUAL' ? '   AUTO   ' : 'MANUAL');
          }}
        />
      </View>
      {
        mode == 'MANUAL' ?
          <View style={{ flex: 0.8 }}>
            <AxisPad
              resetOnRelease={true}
              autoCenter={true}
              onValue={
                ({ x, y }) => {
                  y = -y;
                  var magnitude = Math.sqrt(x * x + y * y);
                  var angle = Math.atan2(x, y) * 180 / Math.PI;
                  magnitude = magnitude > 1 ? 1 : magnitude;
                  angle = (x == 0 && y == 0) ? 0 : angle;
                  speed = magnitude * stats.max_speed;
                  setControls({ angle: angle, speed: speed });
                  postControls.current(angle, speed);
                }
              }>
            </AxisPad>
          </View>
          :
          <View style={{ flex: 0.8 }}>
            <Image 
              style={{width: 512, height: 512}}
              source={{ uri: frame }}
            />
          </View>
      }
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
