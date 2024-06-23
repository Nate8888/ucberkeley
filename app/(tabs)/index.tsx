import React, { useState, useEffect } from 'react';
import { StyleSheet, View, Text, FlatList, Dimensions, StatusBar, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';
import { Audio } from 'expo-av';

const initialNewsData = [
  { id: '1', headline: 'News Headline 1', description: 'Short description of the news article 1...', severity: '10/10', exposure: '5/10', audio_url: 'https://example.com/audio1.mp3' },
  { id: '2', headline: 'News Headline 2', description: 'Short description of the news article 2...', severity: '8/10', exposure: '6/10', audio_url: 'https://example.com/audio2.mp3' },
  { id: '3', headline: 'News Headline 3', description: 'Short description of the news article 3...', severity: '7/10', exposure: '4/10', audio_url: 'https://example.com/audio3.mp3' },
  { id: '4', headline: 'News Headline 4', description: 'Short description of the news article 4...', severity: '9/10', exposure: '3/10', audio_url: 'https://example.com/audio4.mp3' },
  { id: '5', headline: 'News Headline 5', description: 'Short description of the news article 5...', severity: '6/10', exposure: '7/10', audio_url: 'https://example.com/audio5.mp3' },
];

export default function HomeScreen() {
  const [newsData, setNewsData] = useState(initialNewsData);
  const [loading, setLoading] = useState(false);
  const [sound, setSound] = useState(null);

  useEffect(() => {
    const fetchNewsData = async () => {
      try {
        const response = await fetch('https://backpropagators.uc.r.appspot.com/allDisasters');
        const data = await response.json();
        console.log(data);
        const parsedData = data.map((item, index) => ({
          id: String(index + 1),
          headline: item.event,  // Adjust according to actual data structure
          description: item.description ? item.description : item.speaker_summary, // Adjust as necessary
          severity: Math.min(Math.ceil((item.impact.economic_impact + item.impact.environmental_impact + item.impact.health_impact + item.impact.human_impact + item.impact.infrastructure_impact + item.impact.social_impact) / 6 + 1), 10),  // Adjust if actual severity data is available
          exposure: item.awareness ? item.awareness : item.exposure?.awareness,  // Adjust if actual exposure data is available
          audio_url: item.audio_url
        }));

        setNewsData(parsedData.splice(4));
      } catch (error) {
        console.error(error);
      }
    };
    fetchNewsData();
  }, []);

  const fetchMoreNews = () => {
    if (loading) return;

    setLoading(true);
  };

  const playSound = async (url) => {
    if (sound) {
      await sound.unloadAsync();
    }
    const { sound: newSound } = await Audio.Sound.createAsync({ uri: url });
    setSound(newSound);
    await newSound.playAsync();
  };

  const pauseSound = async () => {
    if (sound) {
      await sound.pauseAsync();
    }
  };

  const stopSound = async () => {
    if (sound) {
      await sound.stopAsync();
    }
  };

  useEffect(() => {
    return sound
      ? () => {
          sound.unloadAsync();
        }
      : undefined;
  }, [sound]);

  const renderNewsItem = ({ item }) => (
    <View style={styles.newsItem} key={item.id}>
      <View style={styles.newsText}>
        <ThemedText type="subtitle">{item.headline}</ThemedText>
        <ThemedText>{item.description}</ThemedText>
        <View style={styles.scoresContainer}>
          <ThemedText style={styles.smallText}>Severity: <Text style={styles.scoreValue}>{item.severity}</Text></ThemedText>
          <ThemedText style={styles.smallText}>Exposure: <Text style={styles.scoreValue}>{item.exposure}</Text></ThemedText>
        </View>
        <ThemedText style={styles.readMoreText}>See full details...</ThemedText>
      </View>
      <View style={styles.iconContainer}>
        <TouchableOpacity onPress={() => playSound(item.audio_url)}>
          <Ionicons name="mic-outline" size={24} color="black" />
        </TouchableOpacity>
        <TouchableOpacity onPress={pauseSound}>
          <Ionicons name="pause-outline" size={24} color="black" />
        </TouchableOpacity>
        <TouchableOpacity onPress={stopSound}>
          <Ionicons name="stop-outline" size={24} color="black" />
        </TouchableOpacity>
      </View>
      <Ionicons name="arrow-forward-outline" size={24} color="black" />
    </View>
  );

  return (
    <FlatList
      data={newsData}
      renderItem={renderNewsItem}
      keyExtractor={item => item.id}
      contentContainerStyle={styles.flatListContent}
      onEndReached={fetchMoreNews}
      onEndReachedThreshold={0.5}
      ListHeaderComponent={
        <>
          <ThemedView style={styles.titleContainer}>
            <ThemedText type="title">Hey! I'm TAYLOR👋</ThemedText>
          </ThemedView>
          <ThemedText style={styles.subtitle}>I'm your guide to global disaster knowledge. </ThemedText>
        </>
      }
      ListFooterComponent={
        loading ? (
          <View style={styles.loading}>
            <ThemedText>Loading...</ThemedText>
          </View>
        ) : null
      }
    />
  );
}

const styles = StyleSheet.create({
  flatListContent: {
    paddingTop: StatusBar.currentHeight + 20,
    paddingBottom: 20,
    backgroundColor: '#f0f0f0', // Consistent background color
  },
  titleContainer: {
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 40, // Move down the title text
    backgroundColor: '#f0f0f0', // Background color matching the rest of the page
    paddingVertical: 10,
  },
  subtitle: {
    fontSize: 18,
    textAlign: 'center',
    marginVertical: 10,
    marginTop: 40,
  },
  newsItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 15,
    marginVertical: 10,
    backgroundColor: '#fff',
    borderRadius: 8,
    shadowColor: '#000',
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 2,
    width: Dimensions.get('window').width - 40,
    marginHorizontal: 20,
    position: 'relative',
  },
  newsText: {
    flex: 1,
    marginRight: 10,
  },
  scoresContainer: {
    flexDirection: 'row',
    marginTop: 5,
  },
  smallText: {
    fontSize: 12,
    color: '#888',
    marginRight: 20,
  },
  scoreValue: {
    fontWeight: 'bold',
    color: '#000',
  },
  readMoreText: {
    fontSize: 12,
    color: '#000',
    marginTop: 10,
    textAlign: 'right',
  },
  iconContainer: {
    position: 'absolute',
    top: 10,
    right: 10,
    flexDirection: 'row',
    gap: 5,
  },
  loading: {
    paddingVertical: 20,
    alignItems: 'center',
  },
});
