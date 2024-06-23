import React, { useState, useEffect } from 'react';
import { StyleSheet, View, Text, FlatList, Dimensions, StatusBar } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';

const initialNewsData = [
  { id: '1', headline: 'News Headline 1', description: 'Short description of the news article 1...', severity: '10/10', exposure: '5/10' },
  { id: '2', headline: 'News Headline 2', description: 'Short description of the news article 2...', severity: '8/10', exposure: '6/10' },
  { id: '3', headline: 'News Headline 3', description: 'Short description of the news article 3...', severity: '7/10', exposure: '4/10' },
  { id: '4', headline: 'News Headline 4', description: 'Short description of the news article 4...', severity: '9/10', exposure: '3/10' },
  { id: '5', headline: 'News Headline 5', description: 'Short description of the news article 5...', severity: '6/10', exposure: '7/10' },
];

export default function HomeScreen() {
  const [newsData, setNewsData] = useState(initialNewsData);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchNewsData = async () => {
      try {
        const response = await fetch('https://backpropagators.uc.r.appspot.com/allDisasters');
        const data = await response.json();
        console.log(data);
        const parsedData = data.map((item, index) => ({
          id: String(index + 1),
          headline: item.awareness,  // Adjust according to actual data structure
          description: item.awareness_bullet_points ? item.awareness_bullet_points.join(', ') : '', // Adjust as necessary
          severity: 'Placeholder',  // Adjust if actual severity data is available
          exposure: 'Placeholder',  // Adjust if actual exposure data is available
        }));
        setNewsData(parsedData);
      } catch (error) {
        console.error(error);
      }
    };
    fetchNewsData();
  }, []);

  const fetchMoreNews = () => {
    if (loading) return;

    setLoading(true);
    // setTimeout(() => {
    //   const moreNews = [
    //     {
    //       id: String(newsData.length + 1),
    //       headline: `News Headline ${newsData.length + 1}`,
    //       description: `Short description of the news article ${newsData.length + 1}...`,
    //       severity: 'Placeholder',
    //       exposure: 'Placeholder',
    //     },
    //     {
    //       id: String(newsData.length + 2),
    //       headline: `News Headline ${newsData.length + 2}`,
    //       description: `Short description of the news article ${newsData.length + 2}...`,
    //       severity: 'Placeholder',
    //       exposure: 'Placeholder',
    //     },
    //   ];
    //   setNewsData([...newsData, ...moreNews]);
    //   setLoading(false);
    // }, 1500);
  };

  const renderNewsItem = ({ item }) => (
    <View style={styles.newsItem} key={item.id}>
      <Ionicons name="mic-outline" size={24} color="black" style={styles.speakerIcon} />
      <View style={styles.newsText}>
        <ThemedText type="subtitle">{item.headline}</ThemedText>
        <ThemedText>{item.description}</ThemedText>
        <View style={styles.scoresContainer}>
          <ThemedText style={styles.smallText}>Severity: <Text style={styles.scoreValue}>{item.severity}</Text></ThemedText>
          <ThemedText style={styles.smallText}>Exposure: <Text style={styles.scoreValue}>{item.exposure}</Text></ThemedText>
        </View>
        <ThemedText style={styles.readMoreText}>See full details...</ThemedText>
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
            <ThemedText type="title">What's up, Nate 👋</ThemedText>
          </ThemedView>
          <ThemedText style={styles.subtitle}>See what is going on in the world.</ThemedText>
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
  speakerIcon: {
    position: 'absolute',
    top: 10,
    right: 10,
  },
  loading: {
    paddingVertical: 20,
    alignItems: 'center',
  },
});
