export interface SensorValue {
  last_updated: number;
  topic: string;
  value: string;
}

export interface RaspberryData {
  humidity: SensorValue;
  gas: SensorValue;
}
