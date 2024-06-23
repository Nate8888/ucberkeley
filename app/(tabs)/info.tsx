import React, { useState, useEffect } from 'react';
import { StyleSheet, View, Text, FlatList, Dimensions, StatusBar } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';

export default function InfoScreen() {
  const [infoData, setInfoData] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchInfoData = async () => {
      try {
        const response = await fetch('https://backpropagators.uc.r.appspot.com/allDisasters');
        const data = await response.json();
        console.log(data);
        const parsedData = data.map((item, index) => ({
          id: String(index + 1),
          event: item.event,
          description: item.description || item.speaker_summary,
          impactedAreas: item.impacted_areas?.join(', '),
          awareness: item.awareness,
          speakerSummary: item.speaker_summary,
        }));
        setInfoData(parsedData);
      } catch (error) {
        console.error(error);
      }
    };
    fetchInfoData();
  }, []);

  const renderInfoItem = ({ item }) => (
    <View style={styles.infoItem} key={item.id}>
      <View style={styles.infoText}>
        <ThemedText type="subtitle">{item.event}</ThemedText>
        <ThemedText>{item.description}</ThemedText>
        <ThemedText>Impacted Areas: {item.impactedAreas}</ThemedText>
        <ThemedText>Awareness: {item.awareness}</ThemedText>
        <ThemedText>Speaker Summary: {item.speakerSummary}</ThemedText>
      </View>
    </View>
  );

  return (
    <FlatList
      data={infoData}
      renderItem={renderInfoItem}
      keyExtractor={item => item.id}
      contentContainerStyle={styles.flatListContent}
      onEndReachedThreshold={0.5}
      ListHeaderComponent={
        <>
          <ThemedView style={styles.titleContainer}>
            <ThemedText type="title">Know about what's happening.</ThemedText>
          </ThemedView>
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
  infoItem: {
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
  infoText: {
    flex: 1,
    marginRight: 10,
  },
  loading: {
    paddingVertical: 20,
    alignItems: 'center',
  },
});
